import csv
import os
import re

def load_replacements(file):
    """Load replacements from a CSV file or file-like object."""
    replacements = {}
    
    # Support both file paths and file-like objects
    if isinstance(file, str):
        file = open(file, 'r', encoding='utf-8')
        should_close = True
    else:
        should_close = False
    
    # Read from CSV
    with file as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            hex_value = row["Hex_Value"]
            original_value = row["Original_Value"]
            replacements[hex_value] = original_value

    if should_close:
        file.close()
        
    return replacements

def restore_text(text, replacements):
    """Restore original PII text from hex values using a replacements dictionary."""
    for hex_value, original_value in replacements.items():
        # Restore hex values with the original text
        text = text.replace(hex_value, original_value)
    
    # Remove any "~name~" markers added around names
    text = re.sub(r"~name~(.*?)~name~", r"\1", text)
    return text

def main():
    # Ask the user for input type (terminal paste or file)
    choice = input("Do you want to paste text or provide a txt file path? (paste/file): ").strip().lower()

    if choice == "file":
        text_file_path = input("Enter the path to your .txt file: ").strip()
        if not os.path.exists(text_file_path):
            print("File not found. Exiting.")
            return
        with open(text_file_path, 'r', encoding='utf-8') as file:
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
    else:
        print("Invalid choice. Exiting.")
        return

    # Get the CSV file path
    csv_file_path = input("Enter the path to your CSV file with replacements: ").strip()
    if not os.path.exists(csv_file_path):
        print("CSV file not found. Exiting.")
        return

    # Load replacements from the CSV
    replacements = load_replacements(csv_file_path)

    # Restore the original text by replacing hex values with original values
    restored_text = restore_text(text, replacements)

    # Save or display the restored text
    if choice == "file":
        restored_file_path = f"restored_{os.path.basename(text_file_path)}"
        with open(restored_file_path, 'w', encoding='utf-8') as file:
            file.write(restored_text)
        print(f"Restored text saved to {restored_file_path}")
    else:
        print("Restored text:\n", restored_text)

if __name__ == "__main__":
    main()
