import streamlit

streamlit.set_page_config(
    page_title= "Support Primmosens",
    page_icon="❓",
    layout="wide"
)

page = streamlit.sidebar.radio("Menu",
    [
        "Page d'accueil",
        "Analyse de Prix",
        "Tutoriels BIMoffice",
        "Documents et processus",
        "Assistant BIMoffice",
        "Support Technique"
    ]
)

if page == "Page d'accueil":
    streamlit.title("Support Primmosens")
    streamlit.write("Bienvenue sur la plateforme d'assistance BIMoffice.")

elif page == "Analyse de Prix":
    streamlit.title("Analyse de prix")
    streamlit.write("Retrouvez ici les applications d'analyse de prix.")

elif page == "Tutoriels BIMoffice":
    streamlit.title("Tutoriels BIMoffice")
    streamlit.write("Retrouvez ici les différents guides d'utilisation.")

elif page == "Documents et processus":
    streamlit.title("Documents et processus")
    streamlit.write("Consultez les documents et processus interne de l'entreprise")

elif page == "Assistant BIMoffice":
    streamlit.title("Assistant BIMoffice")
    streamlit.write("Posez vos questions sur le logiciel")

elif page == "Support Technique":
    streamlit.title("Support Technique")
    streamlit.write("Retrouvez les solutions aux problèmes les plus fréquents")

