
import streamlit
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TUTO_DIR = BASE_DIR / "data" / "tutorials"

def getTutorials():
    files = list(TUTO_DIR.rglob("*.md"))
    return sorted(files)

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

def print():
    streamlit.title("Support Primmosens")
    streamlit.write("Bienvenue sur la plateforme d'assistance BIMoffice.")

    tutorials = getTutorials()
    if not tutorials:
        streamlit.warning("Aucun tutoriel dans la base de donnée.")
        return

    names = [ file.stem.replace("_", " ").replace("-", " : ").capitalize()
             for file in tutorials
    ]

    select = streamlit.selectbox(
            "Choisir un tutoriel", options=range(len(tutorials)), format_func=lambda index: names[index],            )
    selectedFiles = tutorials[select]
    content = selectedFiles.read_text(encoding="utf-8")
    streamlit.divider()
    printMarkdown(content, selectedFiles.parent) 

