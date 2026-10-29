import json
from pathlib import Path
import streamlit

BASE_DIR = Path(__file__).resolve().parent.parent
FAQ_PATH = BASE_DIR / "data" / "support" / "faq.json"

def loadFaq():
    if not FAQ_PATH.is_file():
        return []
    with FAQ_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)

def print():
    faq = loadFaq()
    search = streamlit.text_input("Rechercher un problème", placeholder="Exemple: portail, bibliothèque...")
    if not faq:
        streamlit.info("Aucune question disponnible.")
        return
    results = []
    for el in faq:
        text = (el["question"] + " " + el["categorie"] + " " + el["reponse"])
        if search.casefold() in text.casefold():
            results.append(el)
    streamlit.caption(f"{len(results)} résultat(s)")
    for el in results:
        with streamlit.expander(el["question"]):
            streamlit.caption(el["categorie"])
            streamlit.write(el["reponse"])

