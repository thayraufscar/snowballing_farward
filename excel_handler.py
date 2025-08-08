import pandas as pd
from pathlib import Path

TEMPLATE_PATH = "article_template.xlsx"
OUTPUT_PATH = "output/citation_data.xlsx"
BIBTEX_PATH = "output/citations.bibtex"

def create_excel_template():
    path = Path(TEMPLATE_PATH)
    if not path.exists():
        df = pd.DataFrame(columns=["Article Title"])
        df.to_excel(path, index=False)
        print(f"Template created at {TEMPLATE_PATH}")

def load_articles_from_excel():
    df = pd.read_excel(TEMPLATE_PATH)
    return df["Article Title"].dropna().tolist()

def save_results_to_excel(citation_data):
    citations = []
    citers = []
    bibtex_data = []

    for item in citation_data:
        # Add citation summary: article title and total number of citations
        citations.append({
            "Article Title": item["title"],
            "Cited By": item["cited_by"]
        })

        # Add each citing article and check if its BibTeX entry was found
        for citer, bib in zip(item["citers"], item.get("bibtex", [])):
            citers.append({
                "Cited Article": item["title"],
                "Citing Article": citer
            })
            bibtex_data.append({
                "Citing Article": citer,
                "BibTeX Found": bool(bib)
            })

    # Write all data to separate Excel sheets
    with pd.ExcelWriter(OUTPUT_PATH, engine='openpyxl') as writer:
        pd.DataFrame(citations).to_excel(writer, sheet_name="Citations", index=False)
        pd.DataFrame(citers).to_excel(writer, sheet_name="Citing Articles", index=False)
        pd.DataFrame(bibtex_data).to_excel(writer, sheet_name="BibTeX", index=False)

    # Save only found BibTeX entries to the .bibtex file
    with open(BIBTEX_PATH, "w", encoding="utf-8") as f:
        for item, entry in zip(bibtex_data, [bib for article in citation_data for bib in article.get("bibtex", [])]):
            if item["BibTeX Found"]:
                f.write(entry + "\n\n")

