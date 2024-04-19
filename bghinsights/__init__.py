# IMPORTS
import re
from pdfminer.high_level import extract_text


# THESE REGEX PATTERNS WILL BE USED TO EXTRACT VARIOUS INFORMATIONS IN THE EXTRACTED TEXT
# Regex pattern to match the different motion categories
motion_category_pattern = r"(?:Auf die|Die)\s+(Revision|Rechtsbeschwerde|Nichtzulassungsbeschwerde|(?:Beschwerde.*?Nichtzulassung|Beschwerde.*?Revision))"

# Define the pattern to extract the Tenor, which contains the decision
tenor_pattern = r"(beschlossen:|für Recht erkannt:)\s*(.*?)\s*(Gründe:|Tatbestand:|\Z)"

# Define patterns for winning and losing keywords within the Tenor
# The patterns now allow for optional hyphens, new lines within the words, and punctuation after the words
winning_keywords = r"(auf(?:-?\s*)?ge(?:-?\s*)?ho(?:-?\s*)?ben|zu(?:-?\s*)?ge(?:-?\s*)?la(?:-?\s*)?ssen|statt(?:-?\s*)?ge(?:-?\s*)?ge(?:-?\s*)?ben)\b"
losing_keywords = r"(zu(?:-?\s*)?rück(?:-?\s*)?zu(?:-?\s*)?wei(?:-?\s*)?sen|zu(?:-?\s*)?rück(?:-?\s*)?ge(?:-?\s*)?wie(?:-?\s*)?sen|ab(?:-?\s*)?ge(?:-?\s*)?lehnt|ver(?:-?\s*)?wor(?:-?\s*)?fen)\b"

file_path = "E:/Downloads/iv_zr__69-23.pdf" # this is just a sample file path to test if the code is working properly

# FUNCTIONS
# Function to process PDF and extract text from it
def process_pdf(file_path):
    
    try:
        # Extract text using pdfminer.six
        text = extract_text(file_path)

        # Check if the extracted text is empty
        if not text.strip():
            print(f"The file {file_path} contains no text.")
            return None

        # Replace form feed characters (\f) with newline characters (\n)
        text = text.replace('\f', '\n')

        # Strip leading and trailing whitespace from the text
        text = text.strip()

        # Define patterns for filtering out unwanted content
        unwanted_patterns = [
            r"\s*[\u2192\u21d2\u21e8]\s*",  # Arrow symbols: → (right arrow), ⇒ (double right arrow), ⇨ (rightwards white arrow)
        ]

        # Iterate through unwanted patterns and remove matching content
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text)

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    print(text)
    return text

process_pdf(file_path)

# Function to analyze the extracted text content to extract various pieces of information
def analyze_text_content(text):

    # implement extraction function for case number, decision date, guiding principles !IMPORTANT!

    def extract_motion_category(text):
        pattern = re.compile(motion_category_pattern, re.IGNORECASE | re.DOTALL)

        # Search for the pattern in the text
        matches = pattern.findall(text)

        # Check if matches were found
        if matches:
            # Process the matches to replace "Beschwerde ... Nichtzulassung" with "Nichtzulassungsbeschwerde"
            processed_matches = ["Nichtzulassungsbeschwerde" if "Beschwerde" in match else match for match in matches]
            return processed_matches[0]
        else:
            return None
    
    # Extracting Tenor to isolate the decision of the case
    def extract_tenor(text):
         # Search for the pattern in the text
        matches = re.search(tenor_pattern, text, re.IGNORECASE | re.DOTALL)

        if matches:
            # Extract the tenor text from the matched groups
            tenor_text = matches.group(2).strip()
            return tenor_text
        else:
            # If no match is found, return None
            return None
    
    # Function to analyze the court decision inside the tenor
    def analyze_court_decision(tenor_text):
        if tenor_text is None:
            return ""
        # Normalize the text to remove any variations in spacing or line breaks
        normalized_text = ' '.join(tenor_text.split())

        # Flags to indicate the presence of winning or losing keywords
        has_winning_keywords = bool(re.search(winning_keywords, normalized_text))
        has_losing_keywords = bool(re.search(losing_keywords, normalized_text))

        # Determine the decision result based on the keywords found
        if has_winning_keywords and not has_losing_keywords:
            return "Gewonnen"
        elif not has_winning_keywords and has_losing_keywords:
            return "Verloren"
        else:
            return "" # Return NONE or empty string if it does not contain any keywords
    
    motion_category = extract_motion_category(text)
    tenor_text = extract_tenor(text)
    court_decision = analyze_court_decision(tenor_text)

    print(motion_category)
    print(court_decision)

# Now, let's call the `process_pdf` function to extract text from the PDF and then pass that text to `analyze_text_content` function
# This is a sample test checker
text = process_pdf(file_path)
analyze_text_content(text)


# **These are just placeholders for functions**

# Function to establish the connection to Azure Blob Storage
def connect_to_azure_storage():
    # implementation of connection to azure storage to access and write files
    return

# Function to save the extracted text and various information into a Merged JSON File
def save_to_json_file():
    # this function will save extracted text and various information in a Merged JSON File in Azure Blob Storage
    return

# Function to retrieve the json file from Azure Blob Storage
def retrieve_from_json_file():
    # this function will retrieve the merged JSON file from Azure Blob Storage and return the extracted text content and information
    return