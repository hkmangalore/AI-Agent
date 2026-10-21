from agent.state import create_state, add_action, record_observation, next_step, can_continue, finish

state = create_state(

    "Generate a password and tell me the current time"
)

print("initial State")

print(state)

add_action(state, "generate_password")

record_observation(state, "generate_password", "Password:X#8Lm@4P")

next_step(state)

print("\n State after One Iteration")
print (state)

finish(
    state,
    "Password:X#8Lm@4P\nCurrent Time: 10:35 AM"
    )

print("\nFinished State")
print(state)