from memory_extractor import extract_memory

memory = extract_memory(
    "I am learning Newton Law.",
    "Great! All Newton laws are good to learn"
)

print("Extracted Memory:\n ", memory)