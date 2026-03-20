"""
Estrae dati strutturati sulle sagre da un testo usando Ollama (Mistral).
"""

import json
import ollama

MODEL = "mistral"

# Parole che indicano entry spazzatura dal LLM
JUNK_NAMES = {
    "nessuna sagra", "non sono menzionate", "non ci sono sagre",
    "eventi", "imminente", "nessun evento",
}

PROMPT_TEMPLATE = """
Sei un estrattore di dati. Dato il seguente testo, estrai SOLO le sagre, feste e manifestazioni folkloristiche che si svolgono a {paese} o nelle immediate vicinanze.
Ignora completamente sagre o eventi di altri comuni o regioni.
Se non ci sono sagre rilevanti per {paese}, rispondi con un array JSON vuoto: []
Rispondi SOLO con un array JSON valido, nessun testo aggiuntivo.

Formato richiesto:
[
  {{
    "nome": "nome della sagra o festa",
    "comune": "comune dove si svolge",
    "mese_inizio": numero del mese di inizio (1-12) o null,
    "mese_fine": numero del mese di fine (1-12) o null,
    "periodo_descrizione": "descrizione testuale del periodo o null",
    "tipo": "gastronomica/folkloristica/religiosa/musicale/altro"
  }}
]

Testo:
{testo}
"""


def is_junk(entry: dict) -> bool:
    nome = (entry.get("nome") or "").strip().lower()
    if not nome or nome == "null":
        return True
    if any(j in nome for j in JUNK_NAMES):
        return True
    # mese_fine usato come giorno (valore > 12)
    mese_fine = entry.get("mese_fine")
    if isinstance(mese_fine, int) and mese_fine > 12:
        entry["mese_fine"] = None
    mese_inizio = entry.get("mese_inizio")
    # mese_inizio come anno (es. "2006")
    if mese_inizio and str(mese_inizio).isdigit() and int(str(mese_inizio)) > 12:
        entry["mese_inizio"] = None
    return False


def extract_sagre(testo: str, paese: str = "") -> list[dict]:
    """
    Chiama il modello LLM locale e ritorna una lista di sagre estratte,
    filtrate e pulite.
    """
    if not testo.strip():
        return []

    prompt = PROMPT_TEMPLATE.format(testo=testo, paese=paese or "questo luogo")

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"].strip()

        start = content.find("[")
        end = content.rfind("]") + 1
        if start == -1 or end == 0:
            return []

        sagre = json.loads(content[start:end])

        # Pulisci e filtra
        risultati = []
        for s in sagre:
            if is_junk(s):
                continue
            # Normalizza mese come intero
            for campo in ("mese_inizio", "mese_fine"):
                val = s.get(campo)
                if val is not None:
                    try:
                        s[campo] = int(val)
                    except (ValueError, TypeError):
                        s[campo] = None
            risultati.append(s)

        return risultati

    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"  [extractor] Errore parsing JSON: {e}")
        return []


if __name__ == "__main__":
    testo = """
    La Sagra della Porchetta di Ariccia si svolge ogni anno nel mese di settembre.
    La sagra del Vino dei Castelli Romani invece si tiene ad ottobre.
    """
    print(json.dumps(extract_sagre(testo, "Ariccia"), indent=2, ensure_ascii=False))
