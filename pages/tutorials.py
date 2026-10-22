
import streamlit
import unicodedata
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TUTO_DIR = BASE_DIR / "data" / "tutorials"

def getTutorials():
    files = list(TUTO_DIR.rglob("*.md"))
    return sorted(files)

def searchTutorials(tutorials, search):
    if not search.strip():
        return tutorials

    result = []

    search = normalizeText(search.strip())

    for file in tutorials:
        title = file.stem.replace("_", " ").replace("-", " : ")
        content = file.read_text(encoding="utf-8")
        complete = normalizeText(title + " " + content)

        if search in complete:
            result.append(file)
    return result


def printMarkdown(content, folder):
    sep = r"!\[([^\]]*)\]\(([^)]+)\)"
    pos = 0

    for el in re.finditer(sep, content):
        text = content[pos:el.start()]
        if text.strip():
            streamlit.markdown(text)
        desc = el.group(1)
        path = el.group(2)
        file = folder / path
        if file.is_file():
            streamlit.image(str(file))
            if desc:
                streamlit.caption(desc)
        else:
            streamlit.warning(f"Image introuvable : {path}")
        pos = el.end()
    remaining = content[pos:]
    if remaining.strip():
        streamlit.markdown(remaining)


def normalizeText(text):
    text = text.casefold()
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )
    return text


def print():
    streamlit.title("Support Primmosens")
    streamlit.write("Bienvenue sur la plateforme d'assistance BIMoffice.")

    tutorials = getTutorials()
    if not tutorials:
        streamlit.warning("Aucun tutoriel dans la base de donnée.")
        return

    search = streamlit.text_input("Rechercher dans les tutoriels", placeholder="Exemple : marge, lots, bibliothèque, prix...")
    
    result  = searchTutorials(tutorials, search)

    streamlit.caption(f"{len(result)} tutoriel(s) trouvé(s)")

    if not result:
        streamlit.info("Aucun tutoriel ne correspond à votre recherche.")

    names = [ file.stem.replace("_", " ").replace("-", " : ").capitalize()
             for file in result
    ]

    select = streamlit.selectbox(
            "Choisir un tutoriel", options=range(len(result)), format_func=lambda index: names[index],            )
    selectedFiles = result[select]
    content = selectedFiles.read_text(encoding="utf-8")
    streamlit.divider()
    printMarkdown(content, selectedFiles.parent) 

