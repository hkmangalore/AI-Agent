from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("Time Server")

@mcp.tool()

def current_time():
    # Below line is tool description
    """Return the current date and time."""
    print("\n\n<<<<<<<<<<<<<<<<<<<<<Current Time tool called>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

import random
@mcp.tool()
def roll_dice():
    # Below line is tool description
    """Roll a six-sided die and return the result."""

    print("MCP Server -->>>Executing roll_dice tool.")
    return random.randint(1, 6)


import secrets
import string
@mcp.tool()
def generate_password():
    # Below line is tool description
    """Generate a random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(alphabet) for _ in range(12))
    return password

@mcp.tool()
def do_nothing():
    print("MCP Server -->>>Executing do_nothing tool.")

    return "MCP Server -->>>do_nothing tool executed successfully."



if __name__ == "__main__":
    print("Starting MCP server..")
    mcp.run()