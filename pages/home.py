import streamlit

def print():
    streamlit.title("Support Primmosens")
    streamlit.write("Bienvenue sur la plateforme d'assistance BIMoffice.")
    streamlit.subheader("Que voulez vous faire ?")
    
    col1, col2 = streamlit.columns(2)
    with col1:
        streamlit.page_link(
            streamlit.session_state["pages"]["tutorials"],
            label="Consulter les tutoriels BIMoffice",
            icon=":material/menu_book:",
            width='stretch',
        )
        streamlit.page_link(
            streamlit.session_state["pages"]["documents"],
            label="Consulter les documents et processus interne",
            icon=":material/folder:",
            width='stretch',
        )
    with col2:
        streamlit.page_link(
            streamlit.session_state["pages"]["assistant"],
            label="Poser une question à l'assistant",
            icon=":material/smart_toy:",
            width='stretch',
        )
        streamlit.page_link(
            streamlit.session_state["pages"]["support"],
            label="Rechercher une solution",
            icon=":material/build:",
            width='stretch',
        )
