from memory_extractor import extract_memory

memory = extract_memory(
    ###"I am learning Newton Law.",
    ###"Great! All Newton laws are good to learn"

    "What is current time?",
    "The current time is 10 PM"
)

print("Extracted Memory:\n ", memory)