import os
import json
import traceback

def save_json_to_local(directory_path, all_data):
    """
    Save the extracted data to a merged JSON file in a local directory.
    
    Args:
        directory_path (str): The path to the directory where the JSON file will be saved.
        all_data (list): A list containing dictionaries of extracted data from PDF files.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Define the output JSON file path within the output directory
    output_file_path = os.path.join(directory_path, "extracted_json/all_data.json")

    # Save all the data to a single JSON file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=4)
        
        print(f"All data saved to {output_file_path}")

    except Exception as e:
        # Log any errors that occur during file saving
        print(f"Error saving JSON file: {e}")
        traceback.print_exc()  # Print the traceback for detailed error information

def save_json_to_azure(fs, container_name, all_data):
    """
    Save the extracted data to a merged JSON file in an Azure Blob Storage container.
    
    Args:
        fs (adlfs.AzureBlobFileSystem): The Azure Blob FileSystem object representing the connection to Azure Storage.
        container_name (str): The name of the Azure Blob Storage container.
        all_data (list): A list containing dictionaries of extracted data from PDF files.
    """
    # Define the output JSON file path within the container
    output_blob_path = f"{container_name}/extracted_json/all_data.json"

    # Save all the data to a single JSON file in the container
    try:
        with fs.open(output_blob_path, 'wb') as json_blob:
            json_blob.write(json.dumps(all_data, ensure_ascii=False, indent=4).encode('utf-8'))
        
        print(f"All data saved to {output_blob_path}")

    except Exception as e:
        # Log any errors that occur during file saving
        print(f"Error saving JSON file: {e}")
        traceback.print_exc()  # Print the traceback for detailed error information
