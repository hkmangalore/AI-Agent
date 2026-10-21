from agent.state import (
    add_action,
    can_continue,
    create_state,
    finish,
    next_step,
    record_observation,
)


#### This is how multiple action in a statement get executed. For eg: ""Generate a passowod then roll a dice and then give me the time
### Here it breaks the actions into three --> 1. Generate a password 2. Roll a Dice and 3. Current Time
async def run_agent_loop(
    user_request, planner, execute_action, format_answer, tools, client
):
    state = create_state(user_request)

    while can_continue(state):
        print("\nCalling Planner (LLM)\n")
        action = planner(state, tools)
        print("Planner selected:", action)

        if action.strip().upper() == "FINISH":
            finish(state, format_answer(state))
            break

        ###execute_action --> Runs the appropriate tool from MCP server
        observation = await execute_action(action, state, client)
        add_action(state, action)
        record_observation(state, action, observation)
        next_step(state)

    return state