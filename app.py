import streamlit

from pages import (
    home,
    tutorials,
    documents,
    prices,
    assistant,
    support,
)

streamlit.set_page_config(
    page_title= "Support Primmosens",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded",
)

homePage = streamlit.Page(
        home.print,
        title="Accueil",
        icon=":material/home:",
        default=True,
)


tutorialPage = streamlit.Page(
        tutorials.print,
        title="Tutoriels BIMoffice",
        icon=":material/menu_book:",
        url_path="tutorials",
)

documentPage = streamlit.Page(
        documents.print,
        title="Documents et Processus",
        icon=":material/folder:",
        url_path="documents",
)

assistantPage = streamlit.Page(
        assistant.print,
        title="Assistant par message",
        icon=":material/smart_toy:",
        url_path="assistant",
)

supportPage = streamlit.Page(
        support.print,
        title="Support technique",
        icon=":material/build:",
        url_path="support",
)

pricePage = streamlit.Page(
        prices.print,
        title="Analyse des prix",
        icon=":material/bar_chart:",
        url_path="prices",
)

nav = streamlit.navigation(
    {
        "Général" : [
            homePage,
            tutorialPage,
            documentPage,
        ],
        "Outils" : [
            assistantPage,
            pricePage,
        ],
        "Assistance" : [
            supportPage,
        ],
    },
    position="sidebar",
    expanded=True,
)

streamlit.session_state["pages"] = {
        "tutorials": tutorialPage,
        "documents": documentPage,
        "assistant": assistantPage,
        "support": supportPage,
        "prix": pricePage,
        }

nav.run()

