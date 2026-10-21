import os
import logging
import requests
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp_incident_tools")

# Custom Exception Classes
class ToolAPIError(Exception):
    """Base exception for external tool API failures."""
    pass

class RateLimitError(ToolAPIError):
    """Raised when an API rate limit (429) is encountered."""
    pass

class AuthenticationError(ToolAPIError):
    """Raised on authentication (401) or authorization (403) failures."""
    pass

# Retry decorator for transient network failures and rate limits
api_retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, requests.exceptions.RequestException, requests.exceptions.Timeout)),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying API call after failure. Attempt {retry_state.attempt_number}/3..."
    ),
    reraise=True
)

def handle_http_status(response: requests.Response, service_name: str):
    if response.status_code in (401, 403):
        logger.error(f"Authentication failure on {service_name}: {response.status_code} - {response.text}")
        raise AuthenticationError(f"Authentication failed for {service_name}. Verify API credentials/tokens.")
    elif response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "Unknown")
        logger.warning(f"Rate limit hit on {service_name}. Retry-After: {retry_after}s")
        raise RateLimitError(f"Rate limit exceeded on {service_name}.")
    elif response.status_code >= 500:
        logger.error(f"Server error on {service_name}: {response.status_code} - {response.text}")
        response.raise_for_status()

# Initialize FastMCP Server
mcp = FastMCP("Incident-Response-Tools")

# ==========================================
# MCP TOOLS
# ==========================================

@mcp.tool()
@api_retry_policy
def get_servicenow_incident(incident_number: str) -> Dict[str, Any]:
    """Fetch details, caller, priority, state, impacted configuration item (CI), and work notes for a ServiceNow incident.
    
    Args:
        incident_number: The ServiceNow incident identifier (e.g., 'INC0010042').
    """
    instance = os.environ.get("SERVICENOW_INSTANCE")
    user = os.environ.get("SERVICENOW_USER")
    password = os.environ.get("SERVICENOW_PASSWORD")

    if not all([instance, user, password]):
        logger.info(f"Missing ServiceNow credentials. Returning mock fallback data for {incident_number}.")
        return {
            "incident_number": incident_number,
            "short_description": "Production Outage: High latency and 504 errors on Checkout Gateway",
            "state": "In Progress",
            "priority": "1 - Critical",
            "impacted_ci": "checkout-service-prod",
            "assignment_group": "SRE On-Call Core",
            "jira_cross_reference": "INC-1042",
            "repository": "org/checkout-service",
            "description": "504 Gateway Timeout errors spiking above 20% on /api/v1/checkout following recent deployment.",
            "latest_work_notes": "SRE On-Call engaged. Correlating with recent PR deployments in GitHub."
        }

    url = f"https://{instance}.service-now.com/api/now/table/incident"
    params = {
        "sysparm_query": f"number={incident_number}",
        "sysparm_limit": 1,
        "sysparm_display_value": "true"
    }

    try:
        response = requests.get(
            url,
            auth=(user, password),
            headers={"Accept": "application/json"},
            params=params,
            timeout=10.0
        )
        handle_http_status(response, "ServiceNow")
        
        data = response.json()
        results = data.get("result", [])
        
        if not results:
            return {"error": f"ServiceNow incident '{incident_number}' not found."}

        inc = results[0]
        return {
            "incident_number": inc.get("number"),
            "short_description": inc.get("short_description"),
            "state": inc.get("state"),
            "priority": inc.get("priority"),
            "impacted_ci": inc.get("cmdb_ci"),
            "assignment_group": inc.get("assignment_group"),
            "description": inc.get("description"),
            "latest_work_notes": inc.get("work_notes")
        }
    except AuthenticationError as e:
        return {"error": str(e), "action_required": "Verify SERVICENOW_USER and SERVICENOW_PASSWORD credentials."}
    except Exception as e:
        logger.error(f"Failed to query ServiceNow incident {incident_number}: {str(e)}")
        return {"error": f"ServiceNow query failed after retries: {str(e)}"}


@mcp.tool()
@api_retry_policy
def get_jira_issue(issue_key: str) -> Dict[str, Any]:
    """Fetch details, status, description, and metadata for a Jira incident ticket.
    
    Args:
        issue_key: The Jira issue key (e.g., 'INC-1042').
    """
    jira_domain = os.environ.get("JIRA_DOMAIN")
    jira_email = os.environ.get("JIRA_USER_EMAIL")
    jira_token = os.environ.get("JIRA_API_TOKEN")

    if not all([jira_domain, jira_email, jira_token]):
        return {
            "key": issue_key,
            "summary": "High latency on /api/v1/checkout endpoint",
            "status": "In Progress",
            "priority": "P1 - Critical",
            "description": "504 Gateway Timeouts spike up to 25% starting at 14:15 UTC. DB pool exhaustion observed.",
        }

    url = f"https://{jira_domain}/rest/api/3/issue/{issue_key}"
    try:
        response = requests.get(
            url,
            auth=(jira_email, jira_token),
            headers={"Accept": "application/json"},
            timeout=10.0
        )
        handle_http_status(response, "Jira")
        
        if response.status_code == 404:
            return {"error": f"Jira issue '{issue_key}' not found."}
            
        data = response.json()
        return {
            "key": data.get("key"),
            "summary": data["fields"].get("summary"),
            "status": data["fields"]["status"].get("name"),
            "priority": data["fields"]["priority"].get("name"),
            "description": data["fields"].get("description"),
        }
    except AuthenticationError as e:
        return {"error": str(e), "action_required": "Refresh JIRA_API_TOKEN or verify permissions."}
    except Exception as e:
        return {"error": f"Jira query failed after retries: {str(e)}"}


@mcp.tool()
@api_retry_policy
def search_recent_commits(repo_slug: str, branch: str = "main", limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent Git commits for a specific repository and branch.
    
    Args:
        repo_slug: Repository identifier formatted as 'owner/repo' (e.g., 'org/checkout-service').
        branch: Target branch to check. Defaults to 'main'.
        limit: Number of recent commits to return (1-10).
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        return [
            {
                "commit_hash": "a1b2c3d4e5",
                "author": "alex.dev@company.com",
                "message": "fix(db): increase connection pool timeout from 5s to 30s",
                "timestamp": "2026-10-21T14:02:00Z"
            },
            {
                "commit_hash": "f6g7h8i9j0",
                "author": "sam.sre@company.com",
                "message": "feat(checkout): add blocking redis cache verification on cart items",
                "timestamp": "2026-10-21T13:45:00Z"
            }
        ]

    url = f"https://api.github.com/repos/{repo_slug}/commits?sha={branch}&per_page={limit}"
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10.0)
        handle_http_status(response, "GitHub")

        if response.status_code == 404:
            return [{"error": f"Repository '{repo_slug}' or branch '{branch}' not found."}]

        commits = response.json()
        return [
            {
                "commit_hash": c["sha"][:10],
                "author": c["commit"]["author"]["email"],
                "message": c["commit"]["message"],
                "timestamp": c["commit"]["author"]["date"]
            }
            for c in commits
        ]
    except AuthenticationError as e:
        return [{"error": str(e), "action_required": "Verify GITHUB_TOKEN status and scopes."}]
    except Exception as e:
        return [{"error": f"GitHub commit search failed after retries: {str(e)}"}]


@mcp.tool()
@api_retry_policy
def get_commit_diff(repo_slug: str, commit_hash: str) -> Dict[str, Any]:
    """Retrieve file diffs and code patches for a specific commit hash.
    
    Args:
        repo_slug: Repository identifier formatted as 'owner/repo'.
        commit_hash: Full or truncated commit hash ID.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        return {
            "commit_hash": commit_hash,
            "files_changed": ["src/services/cart.ts"],
            "patch": "@@ -45,6 +45,8 @@ export async function validateCart(cartId: string) {\n+  const cacheResult = await redisClient.getSync(`cart:${cartId}`);"
        }

    url = f"https://api.github.com/repos/{repo_slug}/commits/{commit_hash}"
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers, timeout=10.0)
        handle_http_status(response, "GitHub")

        if response.status_code == 404:
            return {"error": f"Commit '{commit_hash}' not found in '{repo_slug}'."}

        data = response.json()
        files = [
            {
                "filename": f["filename"],
                "status": f["status"],
                "patch": f.get("patch", "No patch available")
            }
            for f in data.get("files", [])
        ]
        return {"commit_hash": commit_hash, "files": files}
    except AuthenticationError as e:
        return {"error": str(e), "action_required": "Verify GITHUB_TOKEN status and scopes."}
    except Exception as e:
        return {"error": f"GitHub diff query failed after retries: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="stdio")