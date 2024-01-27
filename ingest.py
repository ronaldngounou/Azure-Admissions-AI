import requests
import pandas as pd
from bs4 import BeautifulSoup
from langchain.document_loaders import RecursiveUrlLoader
from langchain.utils.html import (PREFIXES_TO_IGNORE_REGEX,
                                  SUFFIXES_TO_IGNORE_REGEX)

import sys
import re 
sys.stdout.reconfigure(encoding='utf-8')

# Define a simple extractor function using BeautifulSoup
#def simple_extractor(html: str) -> str:
#    soup = BeautifulSoup(html, "html.parser") #lxml
#    return re.sub(r"\n\n+", "\n", soup.text).strip()
def simple_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract and convert tables to a text representation
    tables = soup.find_all('table')
    table_texts = []
    for table in tables:
        df = pd.read_html(str(table))[0]
        table_texts.append(df.to_string(index=False))

    # Combine table text with the rest of the page text
    text = '\n\n'.join(table_texts) + '\n\n' + soup.text

    # Replace multiple newlines with a single one and return
    return re.sub(r"\n\n+", "\n", text).strip()




def load_college_admission_docs():
    # URLs
    niche_url = "https://www.niche.com/colleges/stony-brook-university-suny/#majors"
    stonybrook_url = "https://www.stonybrook.edu/undergraduate-admissions/apply/first-year.php"
    international_students_url = "https://www.stonybrook.edu/undergraduate-admissions/apply/international.php"


    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # Load documents
    docs_from_niche = RecursiveUrlLoader(url=niche_url, 
                                         max_depth=500, 
                                         extractor=simple_extractor, 
                                         prevent_outside=True, 
                                         use_async=True, 
                                         headers = headers,
                                         link_regex=(
                                                f"href=[\"']{PREFIXES_TO_IGNORE_REGEX}((?:{SUFFIXES_TO_IGNORE_REGEX}.)*?)"
                                                r"(?:[\#'\"]|\/[\#'\"])"
                                                ),
                                                check_response_status=True,
                                         timeout=600).load()
    
    docs_from_stonybrook = RecursiveUrlLoader(url=stonybrook_url, 
                                              max_depth=10000000, 
                                              extractor=simple_extractor, 
                                              prevent_outside=True, 
                                              headers = headers, 
                                              use_async=True, 
                                              timeout=500,
                                              link_regex=(
                                                f"href=[\"']{PREFIXES_TO_IGNORE_REGEX}((?:{SUFFIXES_TO_IGNORE_REGEX}.)*?)"
                                                r"(?:[\#'\"]|\/[\#'\"])"),
                                                check_response_status=True,
                                              ).load()
    docs_from_international_students_stonybrook = RecursiveUrlLoader(url=international_students_url, 
                                              max_depth=10000000, 
                                              extractor=simple_extractor, 
                                              prevent_outside=True, 
                                              headers = headers, 
                                              use_async=True, 
                                              timeout=500,
                                              link_regex=(
                                                f"href=[\"']{PREFIXES_TO_IGNORE_REGEX}((?:{SUFFIXES_TO_IGNORE_REGEX}.)*?)"
                                                r"(?:[\#'\"]|\/[\#'\"])"
                                                ),
                                                check_response_status=True,
                                              ).load()

    # Combine documents
    combined_docs = []
    for doc in docs_from_stonybrook + docs_from_niche + docs_from_international_students_stonybrook:
        # Assuming 'doc' has a 'text' attribute containing the string representation
        combined_docs.append(doc.text if hasattr(doc, 'text') else str(doc))

    # Write to a text file
    with open('scraped_data.txt', 'w', encoding='utf-8') as file:
        for doc in combined_docs:
            file.write(doc + "\n")

    return combined_docs

def remove_trailing_characters(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Using regular expression to replace unwanted characters
    # This will remove occurrences of multiple \n and \t
    processed_content = re.sub(r'[\t\n]+', ' ', content)

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(processed_content)

# Call the function
load_college_admission_docs()

# Replace 'input.txt' and 'output.txt' with your file paths
remove_trailing_characters('scraped_data.txt', 'processed_data.txt')