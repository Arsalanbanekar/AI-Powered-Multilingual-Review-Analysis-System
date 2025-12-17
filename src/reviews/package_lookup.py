# # src/reviews/package_lookup.py

# from typing import Optional
# from google_play_scraper import search

# def get_package_from_app_name(app_name: str, lang: str = "en", country: str = "in") -> Optional[str]:
#     """
#     Given an app name like 'Netflix' or 'WhatsApp',
#     return the first matching package name, e.g. 'com.netflix.mediaclient'.

#     Returns None if no app is found.
#     """
#     app_name = app_name.strip()
#     if not app_name:
#         return None

#     try:
#         results = search(app_name, lang=lang, country=country, n=5)
#         if not results:
#             return None
#         # Pick the top result
#         return results[0].get("appId")
#     except Exception as e:
#         # You can log this if you want
#         print("Error in get_package_from_app_name:", repr(e))
#         return None



# # src/reviews/package_lookup.py

# from typing import Optional
# from google_play_scraper import search

# def get_package_from_app_name(app_name: str, lang: str = "en", country: str = "in") -> Optional[str]:
#     """
#     Given an app name (e.g., 'Netflix', 'WhatsApp'), return the package ID.
#     Uses google-play-scraper's search function.
#     """

#     app_name = app_name.strip()
#     if not app_name:
#         return None

#     try:
#         # Your version supports only: search(query)
#         results = search(app_name)

#         if not results:
#             return None
        
#         # Each result includes "appId"
#         return results[0].get("appId")

#     except Exception as e:
#         print("Error in get_package_from_app_name:", repr(e))
#         return None


# src/reviews/package_lookup.py

from typing import Optional
import requests
from bs4 import BeautifulSoup
import urllib.parse


def get_package_from_app_name(app_name: str, lang: str = "en", country: str = "in") -> Optional[str]:
    """
    Given an app name (e.g., 'Netflix', 'WhatsApp'), try to find the first matching
    app on Google Play and return its package ID (e.g., 'com.netflix.mediaclient').

    This uses direct HTTP request to the Play Store search page and parses the HTML.
    """

    app_name = app_name.strip()
    if not app_name:
        return None

    try:
        query = urllib.parse.quote_plus(app_name)
        # Build search URL
        url = f"https://play.google.com/store/search?c=apps&q={query}&hl={lang}&gl={country}"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print("Play Store search HTTP error:", resp.status_code)
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for links like: /store/apps/details?id=com.netflix.mediaclient&...
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/store/apps/details?id=" in href:
                # Extract the part after 'id='
                # href example: /store/apps/details?id=com.netflix.mediaclient&hl=en&gl=US
                start = href.find("id=") + 3
                end = href.find("&", start)
                if end == -1:
                    package_id = href[start:]
                else:
                    package_id = href[start:end]

                if package_id:
                    print("Found package:", package_id)
                    return package_id

        print("No matching app details link found on search page.")
        return None

    except Exception as e:
        print("Error in get_package_from_app_name:", repr(e))
        return None
