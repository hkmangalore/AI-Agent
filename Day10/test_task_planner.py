from agent.task_planner import decompose_task

user_request = "Generate a passeord and tell me the current time."

tasks = decompose_task(user_request)

print ("Generated Task from the LLM model:")
print("===============")
for task in tasks:
    print(task)
    