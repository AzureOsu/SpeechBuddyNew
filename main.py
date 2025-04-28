import json
import random
from groq import Groq

# Initialize Groq client
groq = Groq(api_key="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")

def load_word_list(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_word_list(filename, word_list):
    with open(filename, 'w') as file:
        json.dump(word_list, file)


def evaluate_pronunciation(target, spoken):
    prompt = f"""
    The child was supposed to say the word: "{target}"
    They said: "{spoken}"

    Assume the role of an AI speech therapist. The user input is determined by speech recognition software which may be inaccurate,
    so be lenient with case, spelling, and extra words. Pass if the target word is present anywhere in the spoken sentence
    (e.g., if the target is "apple", pass for "I said apple pie" or "apple is good").
    Examples:
    - Word: apple, Said: appel pie, Aple is, Opple fruit, apul yum → PASS
    - Word: pin, Said: I spin fast → PASS
    - Word: dog, Said: Dawg → PASS
    - Word: apple, Said: oranges bananas, anul, annele, apend → FAIL
    Consider that the kids have Down syndrome or speech delay, so be very lenient.
    However if the pronunciation of the word and user submitted  word is too different you may fail them
    Only respond with 1 word: either 'PASS' or 'FAIL'. Do not add any extra output.
    """

    try:
        response = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip().upper()

        if result == "PASS":
            return "Pass: Good job!"
        else:
            return f"Fail: Expected '{target}', got '{spoken}'"

    except Exception as e:
        print(f"Evaluation error: {e}")
        return "Fail: Evaluation error"


def generate_therapy_words(correct_words, incorrect_words):
    # Sample word lists (simplified)
    easy_words = ["cat", "dog", "bat", "hat", "mat"]
    medium_words = ["jump", "cake", "fish", "ship", "ball"]
    hard_words = ["rocket", "sunset", "garden", "pencil", "window"]

    # Remove known words from the pool
    available_easy = [w for w in easy_words if w not in correct_words and w not in incorrect_words]
    available_medium = [w for w in medium_words if w not in correct_words and w not in incorrect_words]
    available_hard = [w for w in hard_words if w not in correct_words and w not in incorrect_words]

    # Fallback if lists are empty
    if not available_easy:
        available_easy = easy_words
    if not available_medium:
        available_medium = medium_words
    if not available_hard:
        available_hard = hard_words

    # Select 2 easy, 2 medium, 1 hard
    easy = random.sample(available_easy, min(2, len(available_easy)))
    medium = random.sample(available_medium, min(2, len(available_medium)))
    hard = random.sample(available_hard, min(1, len(available_hard)))

    return easy, medium, hard
