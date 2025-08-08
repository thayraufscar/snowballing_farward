import re

def clean_title(title):
    """
    Normalize the article title by removing formatting and prefix tags.
    """
    if not title:
        return ""

    # Remove tags like [HTML], [PDF], [BOOK], etc.
    title = re.sub(r'^\[\w+\]\s*', '', title)

    # Normalize spaces and case
    title = title.strip().lower()

    # Remove extra internal whitespace
    title = re.sub(r'\s+', ' ', title)

    return title
