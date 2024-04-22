# IMPORTS
import re

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
        
    def extract_case_number(text):
        pattern = re.compile(case_number_pattern, re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(0)
        else:
            return None

    def extract_decision_date(text):
        pattern = re.compile(decision_date_pattern, re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(1)
        else:
            return None

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