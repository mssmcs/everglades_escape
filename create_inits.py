# create_inits.py
import os

# List of directories where __init__.py should exist
# Assumes this script is run from the project root directory
TARGET_DIRS = ['src', 'tests']

print("Checking for __init__.py files...")

for directory in TARGET_DIRS:
    # Construct the full path to the __init__.py file
    init_file_path = os.path.join(directory, '__init__.py')

    # Check if the target directory exists
    if not os.path.isdir(directory):
        print(f"Warning: Directory '{directory}' not found. Skipping.")
        continue

    # Check if the __init__.py file exists
    if not os.path.exists(init_file_path):
        try:
            # Create an empty __init__.py file
            # Using 'a' (append mode) and immediately closing creates an empty file
            # without overwriting if it somehow exists but os.path.exists failed (unlikely).
            with open(init_file_path, 'a'):
                pass
            print(f"Created: '{init_file_path}'")
        except OSError as e:
            print(f"Error creating '{init_file_path}': {e}")
    else:
        print(f"Exists:  '{init_file_path}'")

print("Done.")
