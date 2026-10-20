from tools import (get_current_time, roll_dice, generate_password)

def execute_tool(user_input):
    """
    Executes the appropriate tool based on the user input.

    Args:
        user_input (str): The input provided by the user.

    Returns:
        str: The result from the executed tool or None if no tool was executed.
    """
    if "time" in user_input.lower():
        return get_current_time()

    if "dice" in user_input.lower():
        return f"You rolled {roll_dice()}"

    if "password" in user_input.lower():
        return generate_password()

    return None