from agent.state import (
    add_action,
    add_task,
    complete_task,
    get_pending_tasks,
    all_task_completed,
    can_continue,
    create_state,
    finish,
    next_step,
    record_observation,
)
from agent.task_planner import decompose_task

#### This is how multiple action in a statement get executed. For eg: ""Generate a passowod then roll a dice and then give me the time
### Here it breaks the actions into three --> 1. Generate a password 2. Roll a Dice and 3. Current Time
async def run_agent_loop(
        user_request, planner, execute_action, format_answer, tools, client     ):
    #Create the agent state
    state = create_state(user_request)

    #Breaks the user's request into tasks
    planned_tasks = decompose_task(user_request)

    #Store the tasks into the state
    for task in planned_tasks:
        add_task (state, task)

    print("\n Task Plan")
    print("==================")

    for item in state["tasks"]:
        print("-", item)

    while can_continue(state):
        print("\nCalling Planner (LLM)\n")
        print(f"\n ---Step {state['current_step']+1}---")
        decision = planner(state, tools)
        print("\n Planner decisoin:", decision)

        if decision.strip().upper() == "FINISH":
            finish(state, format_answer(state))
            break


        ### Extract task and tool from decision
        task, tool = parse_decision(decision)

        if not task or not tool:
            add_result(state, "Invalid Planner decision.") 
            next_step(state)
            continue

        state["current_state"] = task

        ###execute_action --> Runs the appropriate tool from MCP server
        observation = await execute_action(action, state, client)        
        # Update state
        add_action(state, action)

        record_observation(state, action, observation)
        # Save observation as intermediate result
        add_result(state, observation)

        #Mark selected task completed
        if not observation.lower().startswith("error"):
            complete_task(state, task)
        else:
            add_result(state, "The previous Action dailed. The planner must reconsider")
        
        next_step(state)

    return state

    def parse_decision(decision):
        task = None
        tool = None

        for line in decision.splitlines():
            line = line.strip()
            
            if line.startswith("TASK:"):
                task = line[5:].strip()
            elif line.startswith("TOOL:"):
                tool = line[5:].strip()    

        return task, tool