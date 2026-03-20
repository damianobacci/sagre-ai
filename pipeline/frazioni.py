"""
Scarica le frazioni (hamlet/village/suburb/locality) di una regione italiana
via Overpass API e le salva in data/frazioni_<regione>.csv

Uso:
    python pipeline/frazioni.py                  # default: Umbria
    python pipeline/frazioni.py Toscana
    python pipeline/frazioni.py "Emilia-Romagna"
"""

import requests
import csv
import sys
import time
from collections import Counter
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
PLACE_TYPES = ["hamlet", "village"]


def build_query(regione: str) -> str:
    place_filters = "\n  ".join(
        f'node["place"="{t}"](area.regione);' for t in PLACE_TYPES
    )
    return f"""
[out:json][timeout:90];
area["name"="{regione}"]["boundary"="administrative"]["admin_level"="4"]->.regione;
(
  {place_filters}
);
out body;
"""


def fetch_frazioni(regione: str) -> list[dict]:
    print(f"Interrogo Overpass API per: {regione}...")
    query = build_query(regione)
    for attempt in range(3):
        try:
            resp = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=120,
                headers={"User-Agent": "sagre-italia-bot/1.0"},
            )
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            print(f"  → {len(elements)} elementi")
            return elements
        except requests.exceptions.HTTPError:
            if resp.status_code == 504 and attempt < 2:
                wait = 15 * (attempt + 1)
                print(f"  Timeout 504, riprovo tra {wait}s... ({attempt + 2}/3)")
                time.sleep(wait)
            else:
                raise
        except requests.exceptions.Timeout:
            if attempt < 2:
                print(f"  Timeout di rete, riprovo... ({attempt + 2}/3)")
                time.sleep(10)
            else:
                raise
    return []


def parse_elements(elements: list[dict]) -> list[dict]:
    rows = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        rows.append({
            "nome": name,
            "nome_it": tags.get("name:it", ""),
            "tipo": tags.get("place", ""),
            "comune": tags.get("is_in:municipality") or tags.get("is_in:city") or "",
            "provincia": tags.get("is_in:province", ""),
            "lat": el.get("lat", ""),
            "lon": el.get("lon", ""),
            "osm_id": el.get("id", ""),
            "wikipedia": tags.get("wikipedia", ""),
            "wikidata": tags.get("wikidata", ""),
        })
    return sorted(rows, key=lambda r: r["nome"])


def save_csv(rows: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["nome", "nome_it", "tipo", "comune", "provincia", "lat", "lon", "osm_id", "wikipedia", "wikidata"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Salvato: {path} ({len(rows)} righe)")


def main():
    regione = sys.argv[1] if len(sys.argv) > 1 else "Umbria"

    elements = fetch_frazioni(regione)
    if not elements:
        print("Nessun elemento trovato — verifica il nome della regione.")
        return

    rows = parse_elements(elements)

    print(f"\nDistribuzione per tipo ({regione}):")
    for tipo, count in Counter(r["tipo"] for r in rows).most_common():
        print(f"  {tipo}: {count}")

    slug = regione.lower().replace(" ", "_").replace("-", "_")
    out_path = Path(__file__).parent.parent / "data" / f"frazioni_{slug}.csv"
    save_csv(rows, out_path)

    print("\nPrime 10 righe:")
    for r in rows[:10]:
        print(f"  {r['nome']} ({r['tipo']}) — {r['comune']}")


if __name__ == "__main__":
    main()
