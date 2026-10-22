import streamlit

def chooseWay(way):
    streamlit.session_state["selectedWay"] = way

def backChosing():
    streamlit.session_state["selectedWay"] = None

def printHome():
    streamlit.subheader("Choisissez un pôle")
    col1, col2 = streamlit.columns(2, gap="medium")

    with col1:
        with streamlit.container(border=True):
            streamlit.subheader("Construction")
            streamlit.write("Consultez les processus et les documents liés aux activités de construction.")
            streamlit.button(
                "Accéder au pôle Construction",
                key="construction",
                use_container_width=True,
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
                use_container_width=True,
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

    with streamlit.container(border=True):
        streamlit.subheader("Cartographie des processus")
        streamlit.info("Les étapes et documents du processus seront intégrés prochainement")

def print():
    streamlit.title("Documents et processus")
    streamlit.write("Retrouver les processus et les documetns interne de Primmosens.")
    way = streamlit.session_state.get("selectedWay")

    if (way is None):
        printHome()
    else:
        printWay(way)

