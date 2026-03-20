"""
Scarica il testo di una pagina web usando Playwright (Chromium headless).
Più affidabile di httpx su siti con JS o anti-bot.
Taglia il testo a MAX_CHARS per non sovraccaricare il prompt LLM.
"""

import re
from playwright.sync_api import sync_playwright

MAX_CHARS = 4000


def scrape_text(url: str) -> str:
    """
    Ritorna il testo pulito della pagina, troncato a MAX_CHARS.
    Ritorna stringa vuota in caso di errore.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000, wait_until="domcontentloaded")

            # Rimuovi elementi inutili
            page.evaluate("""
                document.querySelectorAll('script, style, nav, footer, header, aside, form, iframe')
                    .forEach(el => el.remove());
            """)

            text = page.inner_text("body")
            browser.close()

    except Exception as e:
        print(f"  [scraper] Errore su {url}: {e}")
        return ""

    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_CHARS]


if __name__ == "__main__":
    text = scrape_text("https://www.comune.montefalco.pg.it")
    print(text[:500])
