import os
import json
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
    # Iterate over each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            
            # Read the content of the PDF file
            with open(file_path, 'r', encoding='utf-8') as file:
                pdf_content = file.read()

            # Analyze the text content of the PDF
            analyzed_content = analyze_text_content(pdf_content)

            # Prepare the data to be saved in JSON format
            data_to_save = {
                "case_number": analyzed_content.get("case_number"),
                "decision_date": analyzed_content.get("decision_date"),
                "guiding_principles": analyzed_content.get("guiding_principles"),
                "motion_category": analyzed_content.get("motion_category"),
                "court_decision": analyzed_content.get("court_decision"),
                "senat": analyzed_content.get("senat")
            }

            # Define the path for the JSON file
            json_file_path = os.path.splitext(file_path)[0] + ".json"

            # Save the data to a JSON file
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data_to_save, json_file, ensure_ascii=False, indent=4)

            print(f"Data saved to {json_file_path}")

# Function to retrieve the json file from Azure Blob Storage
def retrieve_from_json_file():
    # this function will retrieve the merged JSON file from Azure Blob Storage and return the extracted text content and information
    return