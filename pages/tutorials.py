
from pandas.api.types import is_file_like
import streamlit
import unicodedata
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TUTO_DIR = BASE_DIR / "data" / "tutorials"

def getTutorials():
    files = list(TUTO_DIR.rglob("*.md"))
    return sorted(files)

def getCategories(tutorials):
    categories = set()
    for file in tutorials:
        category = file.parent.name
        categories.add(category)
    return sorted(categories)

def formatCategory(category):
    names = {
            "etudes_techniques": "Études techniques",
            "appels_offres": "Appels d'offres",
            "projets": "Projets",
            "documents": "Documents",
            }
    return names.get(category, category.replace("_", " ").capitalize)

def openTutorial(file):
    streamlit.session_state["selectedTutorial"] = str(file)

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

    categories = getCategories(tutorials)

    selectedCategory = streamlit.selectbox(
    "Catégorie",
    options=["Toutes les catégories"] + categories,
    format_func=lambda category: (
        category
        if category == "Toutes les catégories"
        else formatCategory(category)
    ),
)
    
    result  = searchTutorials(tutorials, search)

    if selectedCategory != "Toutes les catégories":
        result = [
            file
            for file in result
            if file.parent.name == selectedCategory
        ]

    streamlit.caption(f"{len(result)} tutoriel(s) trouvé(s)")

    if not result:
        streamlit.info("Aucun tutoriel ne correspond à votre recherche.")

    for file in result:
        title = (file.stem.replace("_", " ").replace("-", " : ").capitalize())
        category = formatCategory(file.parent.name)
        with streamlit.container(border=True):
            streamlit.subheader(f"{title}")
            streamlit.caption(f"{category}")
            streamlit.button("Ouvrir le tutoriel",
                             key=f"open_{file}",
                             on_click=openTutorial,
                             args=(file,),
                             use_container_width=True
                            
            )
    selectedPath = streamlit.session_state.get("selectedTutorial")
    if selectedPath:
        selectedFile = Path(selectedPath)

        if selectedFile.is_file():
            streamlit.divider()
            
            if streamlit.button("Fermer le tutoriel"):
                streamlit.session_state["selectedTutorial"] = None
                streamlit.rerun()

            content = selectedFile.read_text(encoding="utf-8")
            printMarkdown(content, selectedFile.parent) 

