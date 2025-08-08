import requests
import time

CROSSREF_API = "https://api.crossref.org/works"

def print_progress(current, total):
    percent = 100 * (current / total)
    bar = '#' * int(percent // 2) + '-' * (50 - int(percent // 2))
    print(f"\rProgress: |{bar}| {percent:.1f}% ({current}/{total})", end='', flush=True)

def get_doi(article_title, retries=3, timeout=30):
    params = {
        "query.title": article_title,
        "rows": 1
    }
    for attempt in range(retries):
        try:
            response = requests.get(CROSSREF_API, params=params, timeout=timeout)
            response.raise_for_status()
            items = response.json().get("message", {}).get("items", [])
            if items:
                return items[0].get("DOI", "")
            return ""
        except Exception as e:
            print(f"\nAttempt {attempt + 1} to get DOI for '{article_title}' failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                print(f"\nFinal failure to retrieve DOI for '{article_title}'")
                return ""

def get_bibtex(doi, retries=3, timeout=30):
    headers = {"Accept": "application/x-bibtex"}
    for attempt in range(retries):
        try:
            response = requests.get(f"https://doi.org/{doi}", headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"\nAttempt {attempt + 1} to get BibTeX for DOI '{doi}' failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                print(f"\nFinal failure to retrieve BibTeX for DOI '{doi}'")
                return ""

def enrich_with_doi_and_bibtex(citation_data):
    total = len(citation_data)
    for idx, item in enumerate(citation_data, start=1):
        item["bibtex"] = []
        for citer in item.get("citers", []):
            doi = get_doi(citer)
            time.sleep(1)  # Avoid overloading the API
            if doi:
                bibtex = get_bibtex(doi)
                item["bibtex"].append(bibtex)
            else:
                item["bibtex"].append("")
        print_progress(idx, total)
    print()  # New line after progress bar completes
    return citation_data
