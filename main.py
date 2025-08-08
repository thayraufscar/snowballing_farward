from scholar_scraper import process_articles
from crossref_lookup import enrich_with_doi_and_bibtex
from excel_handler import (
    create_excel_template,
    load_articles_from_excel,
    save_results_to_excel
)
from progress_bar import print_progress

if __name__ == "__main__":
    print("Creating template (if not exists)...")
    create_excel_template()

    print("Loading articles...")
    articles = load_articles_from_excel()

    print("Processing articles from Google Scholar...")
    citation_data = process_articles(articles, print_progress)

    print("\nEnriching with DOI and BibTeX from Crossref...")
    enriched_data = enrich_with_doi_and_bibtex(citation_data)

    print("Saving results to Excel and BibTeX...")
    save_results_to_excel(enriched_data)

    print("Done. Check the 'output/' folder.")
