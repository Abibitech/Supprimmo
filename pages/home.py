import streamlit

def print():
    streamlit.title("Support Primmosens")
    streamlit.write("Bienvenue sur la plateforme d'assistance BIMoffice.")
    streamlit.subheader("Que voulez vous faire ?")
    
    col1, col2 = streamlit.columns(2)
    with col1:
        streamlit.info("Consulter les tutoriels BIMoffice")
        streamlit.info("Consulter les processus internes")
    with col2:
        streamlit.info("Poser une question à l'assistant")
        streamlit.info("Rechercher une solution")
    streamlit.success("✅ BIMoffice — Version 9.17.31")
