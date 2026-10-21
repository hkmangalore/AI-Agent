Step 1: Set Up Python Environment
=================================================
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate



Step 2: Install Required Dependencies
=================================================
pip install "mcp[cli]" google-genai requests tenacity pydantic


Step 3: Configure Environment Variables
=================================================
# Gemini API Key (Required)
export GEMINI_API_KEY="your-gemini-api-key"

# ServiceNow Credentials (Optional - uses mock data if unset)
export SERVICENOW_INSTANCE="your-instance"
export SERVICENOW_USER="your-user"
export SERVICENOW_PASSWORD="your-password"

# Jira Credentials (Optional - uses mock data if unset)
export JIRA_DOMAIN="your-domain.atlassian.net"
export JIRA_USER_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"

# GitHub Credentials (Optional - uses mock data if unset)
export GITHUB_TOKEN="your-github-pat"



Step 4: Run the MCP Client & Server
=================================================
python client.py