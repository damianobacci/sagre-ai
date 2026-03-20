"""
Pipeline test: prende 10 paesi random dall'Umbria, cerca sagre su DuckDuckGo,
scarica le pagine ed estrae dati strutturati con il modello LLM locale.

Uso:
    python pipeline/main.py
    python pipeline/main.py --regione Toscana --n 10
"""

import csv
import json
import random
import re
import time
import argparse
from pathlib import Path

from search import search_sagre
from scraper import scrape_text
from extractor import extract_sagre


def load_frazioni(regione: str) -> list[dict]:
    slug = regione.lower().replace(" ", "_").replace("-", "_")
    path = Path(__file__).parent.parent / "data" / f"frazioni_{slug}.csv"
    if not path.exists():
        raise FileNotFoundError(f"CSV non trovato: {path}\nEsegui prima: python pipeline/frazioni.py {regione}")
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_pipeline(regione: str, n: int = 10, max_urls: int = 2) -> list[dict]:
    frazioni = load_frazioni(regione)
    campione = random.sample(frazioni, min(n, len(frazioni)))

    print(f"\nPipeline: {n} paesi random da {regione}")
    print("=" * 50)

    tutti_risultati = []
    seen = set()  # chiavi (nome, comune) normalizzate per deduplicazione

    for i, frazione in enumerate(campione, 1):
        paese = frazione["nome"]
        print(f"\n[{i}/{n}] {paese}")

        # 1. Cerca URL su DuckDuckGo (con regione per evitare omonimi)
        urls = search_sagre(paese, regione=regione, max_results=max_urls)
        if not urls:
            print("  Nessun URL trovato, skip.")
            continue
        print(f"  URL trovati: {len(urls)}")

        # 2. Scarica e analizza ogni URL
        for url in urls:
            print(f"  → {url}")
            testo = scrape_text(url)
            if not testo:
                continue

            # 3. Estrai sagre con LLM
            sagre = extract_sagre(testo, paese)
            nuove = 0
            for s in sagre:
                key = (
                    re.sub(r"\s+", " ", (s.get("nome") or "").lower().strip()),
                    re.sub(r"\s+", " ", (s.get("comune") or "").lower().strip()),
                )
                if key in seen:
                    continue
                seen.add(key)
                s["_fonte"] = url
                s["_paese_ricerca"] = paese
                tutti_risultati.append(s)
                nuove += 1
            if nuove:
                print(f"  ✓ {nuove} sagra/e trovata/e")
            else:
                print("  – Nessuna sagra nel testo")

            time.sleep(1)  # pausa tra richieste

        time.sleep(2)  # pausa tra paesi

    return tutti_risultati


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regione", default="Umbria")
    parser.add_argument("--n", type=int, default=10)
    args = parser.parse_args()

    risultati = run_pipeline(args.regione, args.n)

    print(f"\n{'=' * 50}")
    print(f"Totale sagre estratte: {len(risultati)}")

    if risultati:
        out_path = Path(__file__).parent.parent / "data" / "sagre_test.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(risultati, f, indent=2, ensure_ascii=False)
        print(f"Salvato: {out_path}")

        print("\nRisultati:")
        for s in risultati:
            print(f"  {s['nome']} — {s.get('comune', '?')} ({s.get('periodo_descrizione', '?')})")


if __name__ == "__main__":
    main()
