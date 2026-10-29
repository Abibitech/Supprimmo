from functools import Placeholder
import streamlit
from pathlib import Path
import pymupdf
import unicodedata

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSUS_DIR = BASE_DIR / "data" / "processus"

def chooseWay(way):
    streamlit.session_state["selectedWay"] = way

def backChosing():
    streamlit.session_state["selectedWay"] = None

def getDocs(way):
    folder = PROCESSUS_DIR / way
    if not folder.exists():
        return []

    files = list(folder.glob("*.pdf"))
    return sorted(files, key=lambda file: file.name.lower())

def extractText(path, date):
    texts = []
    with pymupdf.open(path) as doc:
        for num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            texts.append({
                "page": num,
                "text": text,
                })
    return texts

def normalizeText(text):
    text = text.casefold()
    text = unicodedata.normalize("NFD", text)
    return "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

def findDocs(files, search):
    if not search.strip():
        return files, {}
    search = normalizeText(search.strip())
    results = []
    pagesFind = {}

    for file in files:
        name = normalizeText(file.stem.replace("_", " "))
        try:
            pages = extractText(str(file), file.stat().st_mtime_ns,)
        except (OSError, ValueError, RuntimeError):
            continue
        isOk = []
        for page in pages:
            text = normalizeText(page["text"])
            if search in text:
                isOk.append(page["page"])
        if search in name or isOk:
            results.append(file)
            pagesFind[str(file)] = isOk
    return results, pagesFind

def printDocs(way):
    files = getDocs(way)
    search = streamlit.text_input("Rechercher un document",
                           placeholder="Exemple : cartographie, contrat, procédure...",
                           key=f"search_{way}",
                           )
    files, pagesFind = findDocs(files, search)
    streamlit.subheader("Documents disponibles")
    streamlit.caption(f"{len(files)} document(s) disponibles")
    if not files:
        streamlit.info("Aucun document disponible pour ce pôle.")
        return

    for file in files:
        title = file.stem.replace("_", " ").capitalize()
        with streamlit.container(border=True):
            streamlit.subheader(f"{title}")
            streamlit.caption(f"Fichier : {file.name}")
            pages = pagesFind.get(str(file), [])
            if pages:
                numbers = ", ".join(str(page) for page in pages)
                streamlit.success(f"Terme trouvé dans les pages : {numbers}")
            
            col1, col2 = streamlit.columns(2)
            with col1:
                if streamlit.button("Visualiser",
                                    key=f"view_{way}_{file.name}",
                                    width='stretch',):
                    streamlit.session_state["selectedPDF"] = str(file)

            with col2:
                streamlit.download_button(
                    label="Télécharger le document",
                    data=file.read_bytes(),
                    file_name=file.name,
                    mime="application/pdf",
                    key=f"download_{way}_{file.name}",
                    width="stretch",
                    )
    selectedPdf = streamlit.session_state.get("selectedPDF")
    if selectedPdf:
        filePdf = Path(selectedPdf)
        if filePdf in files and filePdf.is_file():
            streamlit.divider()
            streamlit.subheader(f"{filePdf.stem}")
            if streamlit.button("Fermer le document"):
                streamlit.session_state["selectedPDF"] = None
                streamlit.rerun()
            streamlit.pdf(filePdf, height=700)



def printHome():
    streamlit.markdown(
        """
        <h3 style="text-align: center;">
            Choisissez un pôle
        </h3>
        """, unsafe_allow_html=True
    )
    col1, col2 = streamlit.columns(2, gap="medium")

    with col1:
        with streamlit.container(border=True):
            streamlit.subheader("Construction")
            streamlit.write("Consultez les processus et les documents liés aux activités de construction.")
            streamlit.button(
                "Accéder au pôle Construction",
                key="construction",
                width="stretch",
                on_click=chooseWay,
                args=("construction",),
            )
    with col2:
        with streamlit.container(border=True):
            streamlit.subheader("Aménagement")
            streamlit.write("Consultez les processus et les documents liés aux activités d'Aménagement.")
            streamlit.button(
                "Accéder au pôle Aménagement",
                key="amenagement",
                width="stretch",
                on_click=chooseWay,
                args=("amenagement",),
            )

def printWay(way):
    streamlit.button(
        "<- Retour aux pôles",
        on_click=backChosing,
    )

    if way == "construction":
        streamlit.header("Construction")
    elif way == "amenagement":
        streamlit.header("Aménagement")

    streamlit.write("Retrouvez ici les processus et les documents associés à ce pole.")
    streamlit.divider()
    printDocs(way)
  

def print():
    streamlit.title("Documents et processus")
    streamlit.write("Retrouver les processus et les documents interne de Primmosens.")
    way = streamlit.session_state.get("selectedWay")

    if (way is None):
        printHome()
    else:
        printWay(way)

