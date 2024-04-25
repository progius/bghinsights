# IMPORTS
import re
import os
from pdf_processor import process_pdf
from datetime import datetime

# Mapping of German month names to numerical representations
month_mapping = {
    "Januar": "01",
    "Februar": "02",
    "März": "03",
    "April": "04",
    "Mai": "05",
    "Juni": "06",
    "Juli": "07",
    "August": "08",
    "September": "09",
    "Oktober": "10",
    "November": "11",
    "Dezember": "12"
}

# THESE REGEX PATTERNS WILL BE USED TO EXTRACT VARIOUS INFORMATIONS IN THE EXTRACTED TEXT

# Regular expression pattern for case number
case_number_pattern = r"(?:\b[IVXLCDM]*[a-zA-Z]+)?\s?\(?(?:[a-zA-Z]+)\)?\s?\d+/\d+\s?[A-Z]?"

# Regular expression pattern for decision date
decision_date_pattern = r"(?:Verkündet am:|vom)\s*(\d{1,2}\.\s*(?:Januar|Februar|März|Marz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4})"

# Regular expression pattern for guiding principles (Leitsätze)
guiding_principles_pattern = r"Nachschlagewerk:"

# Regex pattern to match the different motion categories
motion_category_pattern = r"(?:Auf die|Die)\s+(Revision|Rechtsbeschwerde|Nichtzulassungsbeschwerde|(?:Beschwerde.*?Nichtzulassung|Beschwerde.*?Revision))"

# Define the pattern to extract the Tenor, which contains the decision
tenor_pattern = r"(beschlossen:|für Recht erkannt:)\s*(.*?)\s*(Gründe:|Tatbestand:|\Z)"

# Define patterns for winning and losing keywords within the Tenor
# The patterns now allow for optional hyphens, new lines within the words, and punctuation after the words
winning_keywords = r"(auf(?:-?\s*)?ge(?:-?\s*)?ho(?:-?\s*)?ben|zu(?:-?\s*)?ge(?:-?\s*)?la(?:-?\s*)?ssen|statt(?:-?\s*)?ge(?:-?\s*)?ge(?:-?\s*)?ben)\b"
losing_keywords = r"(zu(?:-?\s*)?rück(?:-?\s*)?zu(?:-?\s*)?wei(?:-?\s*)?sen|zu(?:-?\s*)?rück(?:-?\s*)?ge(?:-?\s*)?wie(?:-?\s*)?sen|ab(?:-?\s*)?ge(?:-?\s*)?lehnt|ver(?:-?\s*)?wor(?:-?\s*)?fen)\b"

# Define the regular expression pattern
senat_pattern = r"Große\s+Senat\s+für\s+Zivilsachen|Große\s+Senat\s+für\s+Strafsachen|Kartellsenat|Senat\s+für\s+Notarsachen|Patentanwaltssachen|Senat\s+für\s+Anwaltssachen|Senat\s+für\s+Landwirtschaftssachen|Senat\s+für\s+Wirtschaftsprüfersachen|Senat\s+für\s+Steuerberater-\s+und\s+Steuerbevollmächtigtensachen|Dienstgericht\s+des\s+Bundes|1.\s+Strafsenat|2.\s+Strafsenat|3.\s+Strafsenat|4.\s+Strafsenat|5.\s+Strafsenat|6.\s+Strafsenat|I.\s+Zivilsenat|II.\s+Zivilsenat|III.\s+Zivilsenat|IV.\s+Zivilsenat|V.\s+Zivilsenat|VI.\s+Zivilsenat|VIa.\s+Zivilsenat|VII.\s+Zivilsenat|VIII.\s+Zivilsenat|IX.\s+Zivilsenat|IXa.\s+Zivilsenat|X.\s+Zivilsenat|Xa.\s+Zivilsenat|XI.\s+Zivilsenat|XII.\s+Zivilsenat|XIII.\s+Zivilsenat|Ermittlungsrichter|Vereinigte\s+Große\s+Senate|Senat\s+für\s+Wirtschaftsprüfersachen"

# Compile the regex pattern
senat_regex = re.compile(senat_pattern)

# Function to analyze the extracted text content to extract various pieces of information
def analyze_text_content(file_obj):
    if hasattr(file_obj, 'read'):  # Check if file_obj is a file-like object
        # Extract the file name directly from the file object
        if hasattr(file_obj, 'name'):
            file_name = os.path.basename(file_obj.name)
        else:
            file_name = "unknown_file.pdf"  # Provide a default name if the file object doesn't have a name attribute
    elif isinstance(file_obj, str):  # Check if file_obj is a string (file path)
        # Extract the file name from the file path
        file_name = os.path.basename(file_obj)
    else:
        raise ValueError("Invalid file object provided.")

    # Process the PDF and extract text
    text = process_pdf(file_obj)

    if not text or not text.strip():
        print(f"The file {file_obj.path} contains no text or text extraction failed.")
        return None, None
    
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
        
    def extract_case_number(text):
        pattern = re.compile(case_number_pattern, re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(0)
        else:
            return None

    def extract_decision_date(text):
        # Define the regular expression pattern for the decision date
        decision_date_pattern = r"(?:Verkündet am:|vom)\s*(\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4})"

        # Search for the decision date pattern in the text
        match = re.search(decision_date_pattern, text)

        if match:
            # Extract the decision date string
            decision_date_str = match.group(1)

            # Convert the month name to its numerical representation
            for month_name, month_number in month_mapping.items():
                if month_name in decision_date_str:
                    decision_date_str = decision_date_str.replace(month_name, month_number)
                    break

            try:
                # Parse the decision date string into a datetime object
                decision_date_obj = datetime.strptime(decision_date_str, "%d. %m %Y")

                # Convert the decision date to UNIX timestamp
                decision_date_unix = int(decision_date_obj.timestamp())
            except ValueError:
                print(f"Error parsing 'decision_date' for file: {file_obj}")
                decision_date_unix = None
        else:
            print(f"No decision date found in the text for file: {file_obj}")
            decision_date_str = None
            decision_date_unix = None

        return decision_date_str, decision_date_unix

    def extract_guiding_principles(text):
        # Define the regular expression pattern to search for guiding principles
        pattern = re.compile(guiding_principles_pattern, re.IGNORECASE | re.DOTALL)
        
        # Search for the pattern in the text
        match = pattern.search(text)
        
        # If a match is found, return "Ja"; otherwise, return "Nein"
        if match:
            return "Ja"
        else:
            return "Nein"
    
    def extract_senat(text):
        match = senat_regex.search(text)
        if match:
            return match.group(0).replace('\n', '').replace('  ',' ')
        else:
            return None

    # Call your extraction functions and return the extracted information
    case_number = extract_case_number(text)
    decision_date, decision_date_unix = extract_decision_date(text)
    guiding_principles = extract_guiding_principles(text)
    motion_category = extract_motion_category(text)
    tenor_text = extract_tenor(text)
    court_decision = analyze_court_decision(tenor_text)
    senat = extract_senat(text)

    return text, {
        "file_name": file_name,
        "case_number": case_number,
        "decision_date": decision_date,
        "guiding_principles": guiding_principles,
        "motion_category": motion_category,
        "court_decision": court_decision,
        "senat": senat,
        "decision_date_unix": decision_date_unix,
        "extracted_text": text  # Include the extracted text in the output dictionary
    }