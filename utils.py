import re
import unicodedata

def clean_title(title):
    """
    Normalize the article title by removing formatting, prefix tags,
    special characters, and accent marks.
    """
    if not title:
        return ""

    # Remove tags like [HTML], [PDF], [BOOK], etc.
    title = re.sub(r'^\[\w+\]\s*', '', title)

    # Normalize quotes/apostrophes
    title = title.replace("’", "'").replace("‘", "'")
    title = title.replace("“", '"').replace("”", '"')

    # Normalize unicode characters to ASCII (remove accents)
    title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')

    # Normalize spaces and case
    title = title.strip().lower()
    title = re.sub(r'\s+', ' ', title)

    return title
