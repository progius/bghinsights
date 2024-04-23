import os
import json
import hashlib
import traceback
from dotenv import load_dotenv
from adlfs import AzureBlobFileSystem
from text_analyzer import analyze_text_content

def connect_to_azure_storage():
    """
    Connect to Azure Storage using the credentials stored in the .env file.
    
    Returns:
        adlfs.AzureBlobFileSystem: A file system object representing the connection to Azure Storage.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get Azure Storage account name, key, and container name from environment variables
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_PDF_CONTAINER")

    if not storage_account_name or not storage_account_key:
        raise ValueError("Azure Storage account name and key must be provided in the .env file.")

    # Initialize AzureBlobFileSystem with the storage account name and key
    fs = AzureBlobFileSystem(account_name=storage_account_name, account_key=storage_account_key)
    
    # If a container name is provided, set it as the default container
    if container_name:
        fs.set_container(container_name)
    
    return fs

# Function to save the extracted text and various information into a Merged JSON File
def save_to_json_files(directory_path):
    # Initialize an empty list to store the extracted data from each PDF file
    all_data = []

    # Iterate over each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            
            # Analyze the text content of the PDF
            extracted_text, analyzed_content = analyze_text_content(file_path)

            # Check if the analysis was successful
            if analyzed_content is None:
                print(f"Analysis failed for file: {file_path}")
                continue

            # Compute MD5 hash of the extracted text
            md5_hash = hashlib.md5(extracted_text.encode()).hexdigest()
            # Use the first 8 characters of the MD5 hash
            md5_short = md5_hash[:15]
            # Convert MD5 hash to integer
            md5_int = int(md5_short, 16)

            # Add the extracted data to the list
            all_data.append({
                "id": md5_int,
                "extracted_text": extracted_text,
                "case_number": analyzed_content.get("case_number"),
                "decision_date_unix": analyzed_content.get("decision_date_unix"),
                "decision_date": analyzed_content.get("decision_date"),
                "guiding_principles": analyzed_content.get("guiding_principles"),
                "motion_category": analyzed_content.get("motion_category"),
                "court_decision": analyzed_content.get("court_decision"),
                "senat": analyzed_content.get("senat")
            })

    # Define the output directory path
    output_directory = os.path.join(directory_path, "extracted_json")

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Define the output JSON file path within the output directory
    output_file_path = os.path.join(output_directory, "all_data.json")

    # Save all the data to a single JSON file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=4)
        
        print(f"All data saved to {output_file_path}")

    except Exception as e:
        # Log any errors that occur during file saving
        print(f"Error saving JSON file: {e}")
        traceback.print_exc()  # Print the traceback for detailed error information