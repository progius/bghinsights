# IMPORTS
import re
import os
import hashlib
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

# Function to extract the case number
def extract_case_number(text):
    pattern = re.compile(case_number_pattern, re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return match.group(0)
    else:
        return None

# Function to extract the decision date
def extract_decision_date(text):
    match = re.search(decision_date_pattern, text)
    if match:
        decision_date_str = match.group(1)
        for month_name, month_number in month_mapping.items():
            if month_name in decision_date_str:
                decision_date_str = decision_date_str.replace(month_name, month_number)
                break
        try:
            decision_date_obj = datetime.strptime(decision_date_str, "%d. %m %Y")
            decision_date_unix = int(decision_date_obj.timestamp())
        except ValueError:
            print("Error parsing 'decision_date'")
            decision_date_unix = None
    else:
        decision_date_str = None
        decision_date_unix = None
    return decision_date_str, decision_date_unix

# Function to extract guiding principles
def extract_guiding_principles(text):
    pattern = re.compile(guiding_principles_pattern, re.IGNORECASE | re.DOTALL)
    match = pattern.search(text)
    if match:
        return "Ja"
    else:
        return "Nein"

# Function to extract motion category
def extract_motion_category(text):
    pattern = re.compile(motion_category_pattern, re.IGNORECASE | re.DOTALL)
    matches = pattern.findall(text)
    if matches:
        processed_matches = ["Nichtzulassungsbeschwerde" if "Beschwerde" in match else match for match in matches]
        return processed_matches[0]
    else:
        return None

# Function to extract tenor text
def extract_tenor(text):
    matches = re.search(tenor_pattern, text, re.IGNORECASE | re.DOTALL)
    if matches:
        return matches.group(2).strip()
    else:
        return None

# Function to analyze court decision
def analyze_court_decision(tenor_text):
    if tenor_text is None:
        return ""
    normalized_text = ' '.join(tenor_text.split())
    has_winning_keywords = bool(re.search(winning_keywords, normalized_text))
    has_losing_keywords = bool(re.search(losing_keywords, normalized_text))
    if has_winning_keywords and not has_losing_keywords:
        return "Gewonnen"
    elif not has_winning_keywords and has_losing_keywords:
        return "Verloren"
    else:
        return ""

# Function to extract the sena
def extract_senat(text):
    match = senat_regex.search(text)
    if match:
        return match.group(0).replace('\n', '').replace('  ',' ')
    else:
        return None

def analyze_text_content(text, filename=None):
    if not text or not text.strip():
        print("The extracted text is empty or extraction failed.")
        return None

    case_number = extract_case_number(text)
    decision_date, decision_date_unix = extract_decision_date(text)
    guiding_principles = extract_guiding_principles(text)
    motion_category = extract_motion_category(text)
    tenor_text = extract_tenor(text)
    court_decision = analyze_court_decision(tenor_text)
    senat = extract_senat(text)

    # Compute MD5 hash of the extracted text
    md5_hash = hashlib.md5(text.encode()).hexdigest()
    # Use the first 8 characters of the MD5 hash
    md5_short = md5_hash[:15]
    # Convert MD5 hash to integer
    md5_int = int(md5_short, 16)

    if filename is not None:
        filename = os.path.basename(filename)

    return {
        "id": md5_int,
        "case_number": case_number,
        "decision_date": decision_date,
        "guiding_principles": guiding_principles,
        "motion_category": motion_category,
        "court_decision": court_decision,
        "senat": senat,
        "decision_date_unix": decision_date_unix,
        "extracted_text": text,
        "filename": filename
    }
