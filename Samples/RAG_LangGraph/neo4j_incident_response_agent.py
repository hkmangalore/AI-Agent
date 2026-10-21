import os
from typing import Annotated, TypedDict, Literal
from pydantic import BaseModel, Field

# LangChain & LangGraph Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import Neo4jGraph
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# ============================================================================
# 1. INITIALIZE GRAPH DB & GEMINI MODEL
# ============================================================================

# Connect to Neo4j Graph Database
graph_db = Neo4jGraph(
    url=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
    username=os.environ.get("NEO4J_USERNAME", "neo4j"),
    password=os.environ.get("NEO4J_PASSWORD", "password")
)

# Refresh schema from DB so Gemini knows the graph structure
graph_db.refresh_schema()
GRAPH_SCHEMA = graph_db.schema

# Initialize Gemini Flash Model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0
)

# ============================================================================
# 2. DEFINE CUSTOM GRAPH DB TOOL
# ============================================================================

class ExecuteCypherInput(BaseModel):
    query: str = Field(
        description="The read-only Cypher query to execute against the Neo4j database."
    )

def query_graph_db(query: str) -> str:
    """Executes a Cypher query against the Neo4j graph database to fetch nodes, edges, and dependencies."""
    try:
        # Sanitize basic write operations for safety
        forbidden = ["CREATE", "DELETE", "SET", "REMOVE", "MERGE", "DROP"]
        if any(keyword in query.upper() for keyword in forbidden):
            return "Error: Only read-only queries (MATCH...RETURN) are allowed."
            
        results = graph_db.query(query)
        if not results:
            return "No matching nodes or paths found in the graph database."
        return str(results)
    except Exception as e:
        return f"Database Query Execution Error: {str(e)}"

# Register tool
tools = [query_graph_db]
llm_with_tools = llm.bind_tools(tools)

# ============================================================================
# 3. LANGGRAPH STATE & AGENT NODES
# ============================================================================

class AgentState(TypedDict):
    # Maintains the conversation turn history
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEM_PROMPT = f"""You are an SRE Incident Response AI Agent integrated with an Enterprise Graph Database.
You analyze production incidents, microservice dependencies, Git commits, and Jira issues.

GRAPH DATABASE SCHEMA:
{GRAPH_SCHEMA}

OPERATIONAL RULES:
1. Translate incoming questions into valid Cypher queries using the provided schema.
2. Use the `query_graph_db` tool to query the database.
3. If a Cypher query errors out or returns empty results, adjust your Cypher syntax and try again.
4. Base your final response strictly on the structural context returned from the database.
"""

def call_agent_model(state: AgentState):
    """Reasoning node that calls Gemini with system instructions and messages history."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    """Conditional edge router: checks if Gemini requested a tool call or is ready to respond."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# ============================================================================
# 4. BUILD & COMPILE LANGGRAPH WORKFLOW
# ============================================================================

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("agent", call_agent_model)
workflow.add_node("tools", ToolNode(tools))

# Add Edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

# Compile LangGraph Agent
graph_agent = workflow.compile()

# ============================================================================
# 5. EXECUTION EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Seed mock data into Neo4j (for testing purposes)
    try:
        graph_db.query("""
            MERGE (s1:Service {name: 'checkout-service'})
            MERGE (s2:Service {name: 'payment-gateway'})
            MERGE (d1:Database {name: 'postgres-primary'})
            MERGE (c1:Commit {hash: 'a1b2c3d', message: 'fix: update db pool connection'})
            MERGE (j1:JiraTicket {key: 'INC-1042', severity: 'P1'})
            
            MERGE (s1)-[:DEPENDS_ON]->(s2)
            MERGE (s1)-[:USES_DB]->(d1)
            MERGE (c1)-[:DEPLOYED_TO]->(s1)
            MERGE (c1)-[:LINKED_TO]->(j1)
        """)
        # Refresh schema after seeding
        graph_db.refresh_schema()
    except Exception as e:
        print(f"Database connection note: {e}")

    # Query the LangGraph agent
    query = "What services depend on or use the database connected to incident INC-1042?"
    
    print(f"\nUser Query: {query}")
    print("-" * 60)

    # Execute graph workflow
    inputs = {"messages": [HumanMessage(content=query)]}
    
    for chunk in graph_agent.stream(inputs, stream_mode="values"):
        latest_msg = chunk["messages"][-1]
        
        # Display Tool Call invocations if made by Gemini
        if hasattr(latest_msg, "tool_calls") and latest_msg.tool_calls:
            for tc in latest_msg.tool_calls:
                print(f"\n[Gemini Tool Call] Executing tool: `{tc['name']}`")
                print(f"Generated Cypher:\n{tc['args']['query']}")
                
        # Display final response from the agent
        elif not getattr(latest_msg, "tool_calls", None) and isinstance(latest_msg, BaseMessage) and latest_msg.type == "ai":
            print("\n[Final Answer Synthesis]:")
            print(latest_msg.content)