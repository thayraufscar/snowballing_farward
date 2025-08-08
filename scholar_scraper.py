from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
from utils import clean_title
from excel_handler import save_results_to_excel

SCHOLAR_LANGUAGE = "pt"
STRINGS = {
    "pt": {"cited_by": "Citado por", "more": "Mais"},
    "en": {"cited_by": "Cited by", "more": "More"},
    "es": {"cited_by": "Citado por", "more": "Más"}
}

BASE_URL = "https://scholar.google.com"
SEARCH_URL = f"{BASE_URL}/scholar?hl={SCHOLAR_LANGUAGE}&q="


def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    service = Service("/usr/local/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)


def is_captcha_page(driver):
    return "sorry/index" in driver.current_url or "captcha" in driver.page_source.lower()


def wait_for_articles(driver, timeout=150):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "gs_ri"))
        )
    except TimeoutException:
        print("⚠️ Timeout waiting for articles to load.")
        return False
    return True


def search_scholar(driver, title):
    driver.get(SEARCH_URL + "+".join(title.strip().split()))
    print("🕵️‍♀️ Please solve the CAPTCHA manually if prompted...")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        if not wait_for_articles(driver):
            return False
    except Exception:
        print("⚠️ Timeout or CAPTCHA not resolved.")
        return False
    return True



def parse_cited_by_link(driver, original_title):
    """
    Search the current Google Scholar result page for the article title.
    If found, return the 'Cited by' link and citation count.

    Parameters:
        driver (webdriver): The Selenium web driver currently on a Scholar search page.
        original_title (str): The title of the article to match.

    Returns:
        tuple(str or None, int or None): The URL of the 'Cited by' link and citation count.
    """
    articles = driver.find_elements(By.CLASS_NAME, "gs_ri")
    for art in articles:
        try:
            # Extract the title from the current search result
            art_title = art.find_element(By.CLASS_NAME, "gs_rt").text

            if clean_title(art_title) == clean_title(original_title):
                links = art.find_elements(By.TAG_NAME, "a")
                for link in links:
                    link_text = link.text
                    if STRINGS[SCHOLAR_LANGUAGE]["cited_by"] in link_text:
                        cited_by_url = link.get_attribute("href")

                        # Extract number of citations from the link text
                        citation_count = int("".join(filter(str.isdigit, link_text)))
                        return cited_by_url, citation_count
        except NoSuchElementException:
            continue
        except ValueError:
            continue

    print(f"[parse_cited_by_link] Article not found: '{original_title}'")
    return None, None


def extract_citing_articles(driver, cited_by_url, original_title):
    titles = []
    seen = set()
    first_page = True
    driver.get(cited_by_url)

    if is_captcha_page(driver):
        print("🔒 CAPTCHA detected again. Please resolve manually...")
        try:
            WebDriverWait(driver, 120).until_not(lambda d: is_captcha_page(d))
            print("✅ CAPTCHA resolved.")
        except Exception:
            print("❌ CAPTCHA not resolved in time.")
            return titles

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "gs_ri"))
            )
        except TimeoutException:
            print("⚠️ No articles found or timeout.")
            break

        articles = driver.find_elements(By.CLASS_NAME, "gs_ri")
        for i, art in enumerate(articles):
            try:
                title = art.find_element(By.CLASS_NAME, "gs_rt").text.strip()
                if first_page and i == 0 and clean_title(title) == clean_title(original_title):
                    continue
                if title and title not in seen:
                    seen.add(title)
                    titles.append(title)
            except NoSuchElementException:
                continue

        first_page = False
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        try:
            more_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, STRINGS[SCHOLAR_LANGUAGE]['more']))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", more_link)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", more_link)
            print("🔁 Clicked 'Mais' link to load more results.")
            time.sleep(2)
        except TimeoutException:
            print("✅ No more 'Mais' link. All results loaded.")
            break
        except Exception as e:
            print(f"⚠️ Failed to click 'Mais' link: {e}")
            break

    return titles


def process_articles(articles, progress_callback):
    driver = start_driver()
    results = []

    for i, title in enumerate(articles):
        if i != 0 and i % 5 == 0:
            driver.quit()
            print(f"🔄 Restarting browser before starting block {i // 5 + 1}...")
            time.sleep(10)
            driver = start_driver()

        attempt = 0
        max_attempts = 2
        while attempt < max_attempts:
            try:
                print(f"\n🔍 Searching for: {title} (attempt {attempt + 1})")
                success = search_scholar(driver, title)
                citers = []
                citation_count = 0

                if success:
                    cited_by_link, _ = parse_cited_by_link(driver, title)
                    if cited_by_link:
                        citers = extract_citing_articles(driver, cited_by_link, title)
                        citation_count = len(citers)  # count citers instead of link text number
                    else:
                        print("ℹ️ 'Cited by' link not found.")
                        citers = []
                        citation_count = 0
                else:
                    print("⚠️ Search skipped due to unresolved CAPTCHA.")

                if (not success or citation_count == 0) and attempt == 0:
                    attempt += 1
                    time.sleep(5)
                    continue

                results.append({
                    "title": title,
                    "cited_by": citation_count,
                    "citers": citers
                })
                break

            except Exception as e:
                print(f"\n❌ Error processing article '{title}': {e}")
                results.append({
                    "title": title,
                    "cited_by": 0,
                    "citers": []
                })
                break

        if (i + 1) % 5 == 0 or (i + 1) == len(articles):
            print("💾 Saving partial results...")
            save_results_to_excel(results)
            time.sleep(5)

        delay = 8 + (i % 5)
        if i % 5 == 0:
            delay += 5
        time.sleep(delay)

        progress_callback(i + 1, len(articles))

    driver.quit()
    return results

