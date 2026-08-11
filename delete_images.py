import os
from pathlib import Path

def remove_images_from_folder(folder_path):
    # Define common image extensions to target (case-insensitive)
    image_extensions = {'.jpg'}
    
    # Convert string path to a Path object
    target_dir = Path(folder_path)
    
    # Check if the folder actually exists
    if not target_dir.exists():
        print(f"Error: The folder '{folder_path}' does not exist.")
        return
        
    if not target_dir.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return

    deleted_count = 0
    
    # Iterate through all items in the folder
    for file_path in target_dir.iterdir():
        # Check if it is a file and if its extension matches our image list
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            try:
                # Delete the image file
                file_path.unlink()
                print(f"Deleted: {file_path.name}")
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {file_path.name}. Error: {e}")
                
    print(f"\nCleanup complete. Total images removed: {deleted_count}")

# --- Configuration ---
# Replace this with the actual path to your folder
YOUR_FOLDER_PATH = r"C:\Users\Venis\Documents\GitHub Projects\Begineer-AWS-Rekognition-Project\labeled_frames" 

# Execute the function
remove_images_from_folder(YOUR_FOLDER_PATH)
