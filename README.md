# Snowballing App

## Overview

This application automates a backward snowballing process using Google Scholar and Crossref.

## Features

- Load article titles from an Excel template.
- Retrieve citation count and citing articles from Google Scholar.
- Lookup DOI and BibTeX entries via Crossref.
- Export results to Excel and `.bibtex` file.

## Installation

1. Clone the repository or unzip the provided archive.
2. Create a Python environment and install dependencies:

```bash
pip install -r requirements.txt
```

3. Edit article_template.xlsx to include your article titles.

## Execution

```bash
python main.py
```

## Output

Excel file: output/citation_data.xlsx
- Sheet "Citations": article titles and citation count
- Sheet "Citing Articles": list of citing articles
- Sheet "BibTeX": status of BibTeX retrieval

BibTeX file: output/citations.bibtex

## Notes

- Make sure your internet connection is stable.
- Avoid overloading Google Scholar to prevent temporary blocks.
- Use proxies or APIs for heavy usage.
