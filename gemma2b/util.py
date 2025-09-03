# This script renames .doc files in a specified directory by replacing spaces in their filenames with underscores.
import platform
import os
import re

print(platform.architecture())

# Rename 59 .doc files by replacing spaces with underscores
directory_path = "c:/personal/_gemma/customdocs/raw/dogs_breeds_doc/" # Replace with your actual directory path

try:
    for filename in os.listdir(directory_path):
        # Construct the full old path
        old_file_path = os.path.join(directory_path, filename)

        # Check if it's a file (not a directory)
        if os.path.isfile(old_file_path) and filename.endswith('.doc') and ' ' in filename :
            # Create new filename by replacing spaces with underscores
            new_filename = re.sub(r' ', '_', filename)
            new_file_path = os.path.join(directory_path, new_filename)
            # Rename the file
            os.rename(old_file_path, new_file_path)
        else:
            print(f"Skipped '{filename}' (not a .doc file or no spaces found)")
except FileNotFoundError:
    print(f"Error: Directory not found at '{directory_path}'")
except Exception as e:
    print(f"An error occurred: {e}")