The Day09 folder : The Agent behave like this
        User
        |
        |
        Take Decomposition
        |
        |
        Tasks
        |
        |
        Planner --> Task + Tools
        |
        |
        Observation
        |
        |
        Planner Again


Practically, we will modify the Day 9 agent so that it can:
        1. Understand a larger Task
        2. Break it into smaller Task
        3. Execture those tasks one by one
        4. Store intermediate results
        5. Evaluate the situation after every Action
        6. Change its plan when necessary
        7. Stop when the overall goal is achieved

For Eg:
The user prompt like "Create a Python report"

can become:
        1. Research Python
        2. Summarize the information
        3. Write the report
        4. Save the report

        