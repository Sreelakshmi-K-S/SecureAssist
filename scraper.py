import os
import requests
import hashlib
from bs4 import BeautifulSoup

try:
    from html2image import Html2Image
    HTI_AVAILABLE = True
except ImportError:
    HTI_AVAILABLE = False

# 1. Define Common Windows Paths for Browsers
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

# 2. Setup Output Directory
PREVIEW_DIR = os.path.join('static', 'previews')
if not os.path.exists(PREVIEW_DIR):
    os.makedirs(PREVIEW_DIR)

# 3. Initialize Browser with Safe Mode
hti = None
if HTI_AVAILABLE:
    browser_exe = None
    if os.path.exists(CHROME_PATH):
        browser_exe = CHROME_PATH
    elif os.path.exists(EDGE_PATH):
        browser_exe = EDGE_PATH

    if browser_exe:
        try:
            hti = Html2Image(browser_executable=browser_exe, output_path=PREVIEW_DIR)
            print(f"✅ Browser found at: {browser_exe}")
        except Exception as e:
            print(f"⚠️ Error initializing browser: {e}")
    else:
        print("❌ No browser found. Screenshot features will be disabled.")


def scrape_url(url):
    """Scrapes site metadata and safely attempts a screenshot.
    All returned data is JSON-serializable (no BS4 objects).
    """
    data = {
        "title": "Unknown Title",
        "description": "No description available.",
        "text": "",
        "image_url": None,
        "forms": [],   # list of plain dicts — NOT BS4 Tag objects
        "links": {"internal": 0, "external": 0},
        "status": "success"
    }

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SecurityGuard/1.0'}
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract page title
        title_tag = soup.find('meta', property='og:title') or soup.find('title')
        data["title"] = (
            title_tag.get('content') if hasattr(title_tag, 'get') and title_tag.get('content')
            else (title_tag.text.strip() if title_tag else "No Title")
        )

        # Extract meta description
        desc_tag = (
            soup.find('meta', property='og:description')
            or soup.find('meta', attrs={'name': 'description'})
        )
        data["description"] = desc_tag.get('content', 'No description available.') if desc_tag else "No description available."

        # Extract visible text (capped to avoid oversized sessions)
        data["text"] = soup.get_text(separator=' ', strip=True)[:3000]

        # Serialize form info as plain dicts (NOT raw BS4 Tags)
        raw_forms = soup.find_all('form')
        data["forms"] = [
            {
                'action': f.get('action', ''),
                'method': f.get('method', 'get'),
                'has_password': bool(f.find('input', {'type': 'password'}))
            }
            for f in raw_forms
        ]

        # Link analysis
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            if url in href or href.startswith('/') or href.startswith('#'):
                data["links"]["internal"] += 1
            else:
                data["links"]["external"] += 1

        # Screenshot (optional)
        if hti:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            img_name = f"preview_{url_hash}.png"
            hti.screenshot(url=url, save_as=img_name, size=(1280, 720))
            data["image_url"] = f"previews/{img_name}"

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        data["status"] = "error"
        data["error"] = str(e)
        data["description"] = f"Could not analyze site: {str(e)}"

    return data