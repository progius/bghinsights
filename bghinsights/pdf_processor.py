from pdfminer.high_level import extract_text

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
    
    return text