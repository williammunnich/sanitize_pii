import re
import random
import csv
import os
import nltk
from nltk.corpus import words, names

# Ensure the necessary NLTK corpora are downloaded
nltk.download('words', quiet=True)
nltk.download('names', quiet=True)

# Initialize English words and names sets from NLTK
english_words = set(words.words())
male_names = set(names.words('male.txt'))
female_names = set(names.words('female.txt'))
all_names = male_names | female_names  # Combine male and female names

# Function to generate an 8-digit hex value
def generate_hex():
    return f"{random.randint(0, 0xFFFFFFFF):08X}"

# Check if a value is already an 8-digit hex string
def is_hex(value):
    return bool(re.fullmatch(r"[A-Fa-f0-9]{8}", value))

# Check if a word is an English word
def is_english_word(word):
    return word.lower() in english_words

# Check if a word is a common name
def is_name(word):
    return word in all_names

# Function to find and replace PII in text, ensuring unique replacements
def replace_pii(text, pii_patterns):
    replacements = {}
    processed_text = text

    for label, pattern in pii_patterns.items():
        matches = list(re.finditer(pattern, processed_text))  # Collect matches to avoid modifying text during iteration
        for match in matches:
            original_value = match.group(0)

            # Skip if this original value is already an 8-digit hex, or is an English word but not a name
            if original_value in replacements or is_hex(original_value) or (is_english_word(original_value) and not is_name(original_value)):
                continue

            # Generate a new hex value for the original PII
            hex_value = generate_hex()
            replacements[original_value] = (hex_value, label)

            # Surround names with ~name~ and replace all instances
            if label == "name":
                modified_value = f"~name~{hex_value}~name~"
            else:
                modified_value = hex_value
            
            processed_text = re.sub(re.escape(original_value), modified_value, processed_text)

    return processed_text, replacements

# Main program
def main():
    # Define PII patterns (regex) for phone numbers, emails, etc.
    pii_patterns = {
        "phone_number": r'\b(\+?1[-.\s]?|0)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        "name": r'\b[A-Z][a-z]*[_\s][A-Z][a-z]*\b',  # Updated pattern to match both "First Last" and "First_Last"
        "password": r'\b(?:password[:=]?\s*([A-Za-z0-9@#$%^&+=]{8,}))|([A-Za-z0-9@#$%^&+=]{8,})\b'  # Only replace actual password values
    }

    # Ask the user for input type (terminal paste or file)
    choice = input("Do you want to paste text or provide a txt file path? (paste/file): ").strip().lower()

    if choice == "file":
        file_path = input("Enter the path to your .txt file: ").strip()
        if not os.path.exists(file_path):
            print("File not found. Exiting.")
            return
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    elif choice == "paste":
        print("Paste your text below. Press Enter and then Ctrl+D (or Ctrl+Z on Windows) when done:")
        text = ""
        while True:
            try:
                line = input()
            except EOFError:
                break
            text += line + "\n"
        file_path = "terminal_paste"
    else:
        print("Invalid choice. Exiting.")
        return

    # Replace PII in text and collect replacements
    modified_text, replacements = replace_pii(text, pii_patterns)

    # Write replacements to CSV file
    csv_file_path = "pii_replacements.csv"
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Hex_Value", "Original_Value", "PII_Type", "Source_File"])
        for original_value, (hex_value, pii_type) in replacements.items():
            writer.writerow([hex_value, original_value, pii_type, file_path])

    # Save modified text back if it was from a file
    if choice == "file":
        modified_file_path = f"modified_{os.path.basename(file_path)}"
        with open(modified_file_path, 'w', encoding='utf-8') as modified_file:
            modified_file.write(modified_text)
        print(f"Modified text saved to {modified_file_path}")
    else:
        print("Modified text:\n", modified_text)

    print(f"Replacements logged in {csv_file_path}")

if __name__ == "__main__":
    main()
