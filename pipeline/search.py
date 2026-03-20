"""
Cerca sagre per un dato paese/frazione usando DuckDuckGo (ddgs library).
Restituisce una lista di URL rilevanti.
"""

from ddgs import DDGS

SKIP_DOMAINS = {"facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com"}


def search_sagre(paese: str, regione: str = "", max_results: int = 3) -> list[str]:
    """
    Cerca 'sagra <paese> <regione>' su DuckDuckGo e ritorna fino a max_results URL.
    """
    query = f"sagra {paese} {regione}".strip()
    results = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results * 2):
                href = r.get("href", "")
                if not href.startswith("http"):
                    continue
                domain = href.split("/")[2].replace("www.", "")
                if any(skip in domain for skip in SKIP_DOMAINS):
                    continue
                if href not in results:
                    results.append(href)
                if len(results) >= max_results:
                    break
    except Exception as e:
        print(f"  [search] Errore per '{paese}': {e}")

    return results


if __name__ == "__main__":
    urls = search_sagre("Montefalco", max_results=3)
    for u in urls:
        print(u)
