import random
import secrets
import string

from datetime import datetime

def get_current_time():
    "Return the current date and time."
    return datetime.now().strftime("%d-%m-%Y %I:%M%S %p")


def roll_dice():
    "Return a random number between 1 and 6."
    return random.randint(1,6)

def generate_password(length=12):
    "Generate a secure random password."
    characters=(
        string.ascii_letters +
        string.digits +
        string.punctuation
    )
    password=""
    for _ in range(length):
        password+=secrets.choice(characters)
        
    return password


def read_text_file(filename):
    "Read the contents of a text file and return it as a string."
    try:
        with open(filename, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"An error occurred: {e}"