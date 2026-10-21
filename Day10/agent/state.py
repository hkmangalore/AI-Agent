def create_state(user_request, max_steps=5):

    return {
        "user_request": user_request,
        "tasks": [],
        "current_task":None,
        "current_step":0,
        "max_steps": max_steps,
        "actions": [],
        "observations": [],
        "results": [],
        "finished": False,
        "final_answer": ""
    }

def add_action(state, action):
    state["actions"].append({action})

def add_task(state, task):
    state["tasks"].append({
        "task":task,
        "status": "pending"
    })

def complete_task(state, task):
    for item in state["tasks"]:
        if items["task"] == task:
            item["status"] = "completed"
            return

def add_result(state, result):
    state["results"].append(result)

def get_pending_tasks(state):
    return [
        item["task"]
        for item in state["tasks"]
            if item["status"] == "pending" 
        ]

def all_task_completed(state):
    return all(
        item["status"]=="completed"
        for item in state["tasks"]
    )


def record_observation(state, action, observation):
    state["observations"].append(
        {
           "step": state["current_step"],
           "action": action,
           "observation": observation
           #Note: here observation means result<"observaition": observation>
        }
    )

def next_step(state):
    state["current_step"]+=1


def can_continue(state):
    return(
        not state["finished"]
        and 
        state["current_step"] < state ["max_steps"]
    )



def finish(state, answer):
    state["final_answer"] = answer
    state["finished"]= True
    