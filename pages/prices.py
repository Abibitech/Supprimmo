import hashlib

import pandas as pd
import streamlit as st

from utils.excelReader import readExcel


def convertir_nombre(valeur):
    if pd.isna(valeur):
        return 0.0

    texte = str(valeur).replace("€", "")
    texte = texte.replace(" ", "").replace(",", ".")

    try:
        return float(texte)
    except ValueError:
        return 0.0


def euro(valeur):
    return f"{valeur:,.2f} €".replace(",", " ").replace(".", ",")


def analyser_excel(data):
    entete = None

    for index, ligne in data.iterrows():
        valeurs = [str(v).strip() for v in ligne]

        if "Code" in valeurs and "Désignation" in valeurs:
            entete = index
            break

    if entete is None:
        raise ValueError("En-tête BIMoffice introuvable.")

    lignes = data.iloc[entete + 1:].reset_index(drop=True)

    articles = []

    lot = ""
    nom_lot = ""
    bordereau = "Sans bordereau"

    for _, ligne in lignes.iterrows():
        valeurs = ligne.tolist()

        if len(valeurs) < 13:
            continue

        code = str(valeurs[0]).strip()
        designation = str(valeurs[1]).strip()
        quantite = convertir_nombre(valeurs[2])
        unite = str(valeurs[3]).strip()
        prix_unitaire = convertir_nombre(valeurs[4])
        total = convertir_nombre(valeurs[5])
        identifiant = str(valeurs[12]).strip()

        if identifiant.endswith("_Lot"):
            lot = code
            nom_lot = designation
            bordereau = "Sans bordereau"

        elif identifiant.endswith("_Bord"):
            bordereau = designation

        elif identifiant.endswith("_Art"):
            articles.append({
                "Lot": lot,
                "Nom du lot": nom_lot,
                "Bordereau": bordereau,
                "Code": code,
                "Désignation": designation,
                "Quantité": quantite,
                "Unité": unite,
                "Prix achat unitaire": prix_unitaire,
                "Total achat HT": total,
            })

    return pd.DataFrame(articles)


def print():
    st.title("Analyse des prix")

    st.write(
        "Importez un estimatif Excel pour calculer "
        "vos prix de vente."
    )

    fichier = st.file_uploader(
        "Importer un fichier Excel",
        type=["xlsx"],
    )

    if fichier is None:
        st.info("Sélectionnez un fichier Excel BIMoffice.")
        return

    try:
        data = readExcel(fichier)
        articles = analyser_excel(data)

    except Exception as erreur:
        st.error(f"Erreur de lecture : {erreur}")
        return

    if articles.empty:
        st.warning("Aucun article détecté.")
        return

    total_achat = articles["Total achat HT"].sum()

    fichier_id = hashlib.sha256(
        fichier.getvalue()
    ).hexdigest()[:12]

    st.divider()

    st.subheader("Objectif commercial")

    mode = st.radio(
        "Mode de calcul",
        [
            "Choisir un pourcentage de marge",
            "Choisir un prix de vente total",
        ],
        horizontal=True,
    )

    if mode == "Choisir un pourcentage de marge":

        marge_cible = st.slider(
            "Marge globale recherchée (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=0.5,
        )

        vente_cible = total_achat * (1 + marge_cible / 100)

    else:

        prix_saisi = st.text_input(
            "Prix de vente total recherché HT (€)",
            value=euro(total_achat * 1.20),
            key=f"prix_cible_{fichier_id}",
        )

        try:
            vente_cible = float(
                prix_saisi
                .replace("€", "")
                .replace(" ", "")
                .replace("\u202f", "")
                .replace("\xa0", "")
                .replace(",", ".")
            )

            if vente_cible < 0:
                st.error("Le prix de vente ne peut pas être négatif.")
                st.stop()

        except ValueError:
            st.error("Saisis un montant valide.")
            st.stop()

        if total_achat > 0:
            marge_cible = (
                vente_cible / total_achat - 1
            ) * 100
        else:
            marge_cible = 0.0

    lots = list(
        articles.groupby(
            ["Lot", "Nom du lot"],
            sort=False,
        )
    )

    marge_initiale = max(
        -50.0,
        min(200.0, float(marge_cible)),
    )

    if st.session_state.get("prix_fichier_id") != fichier_id:
        st.session_state["prix_fichier_id"] = fichier_id
        st.session_state["prix_marges_modifiees"] = False
        st.session_state["prix_modification_visible"] = False

    marges_lots = {}

    for (numero, nom), lot in lots:
        cle = f"marge_lot_{fichier_id}_{numero}"

        if cle not in st.session_state:
            st.session_state[cle] = marge_initiale

        marges_lots[numero] = st.session_state[cle]

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total achat HT",
        euro(total_achat),
    )

    col2.metric(
        "Objectif de vente HT",
        euro(vente_cible),
    )

    col3.metric(
        "Marge brute recherchée",
        euro(vente_cible - total_achat),
    )

    st.divider()

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Répartition des marges")

    with col2:
        if st.button(
            "Modifier la répartition"
            if not st.session_state["prix_modification_visible"]
            else "Masquer les réglages",
            width="stretch",
        ):
            st.session_state["prix_modification_visible"] = (
                not st.session_state["prix_modification_visible"]
            )
            st.rerun()

    if st.session_state["prix_modification_visible"]:

        st.caption(
            "Ajustez les marges par lot pour atteindre "
            "le prix de vente recherché."
        )

        if st.button(
            "Réinitialiser les marges",
            width="stretch",
        ):
            for (numero, nom), lot in lots:
                cle = f"marge_lot_{fichier_id}_{numero}"
                st.session_state[cle] = marge_initiale

            st.session_state["prix_marges_modifiees"] = False
            st.rerun()

        for (numero, nom), lot in lots:

            cle = f"marge_lot_{fichier_id}_{numero}"

            col1, col2 = st.columns([3, 1])

            with col1:
                st.slider(
                    f"Lot {numero} — {nom}",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    key=cle,
                )

            with col2:
                achat_lot = lot["Total achat HT"].sum()

                vente_lot = achat_lot * (
                    1 + st.session_state[cle] / 100
                )

                st.metric(
                    "Vente HT",
                    euro(vente_lot),
                )

            marges_lots[numero] = st.session_state[cle]

        st.session_state["prix_marges_modifiees"] = True

    if not st.session_state["prix_marges_modifiees"]:
        for (numero, nom), lot in lots:
            cle = f"marge_lot_{fichier_id}_{numero}"
            st.session_state[cle] = marge_initiale
            marges_lots[numero] = marge_initiale

    articles["Marge %"] = articles["Lot"].map(
        marges_lots
    )

    articles["Prix vente unitaire"] = (
        articles["Prix achat unitaire"]
        * (1 + articles["Marge %"] / 100)
    )

    articles["Total vente HT"] = (
        articles["Total achat HT"]
        * (1 + articles["Marge %"] / 100)
    )

    vente_simulee = articles["Total vente HT"].sum()
    ecart = vente_simulee - vente_cible

    st.divider()

    st.subheader("Résultats de la simulation")

    if abs(ecart) < 0.01:
        st.success("Objectif commercial atteint.")

    elif ecart < 0:
        st.warning(
            f"Il reste {euro(abs(ecart))} à répartir "
            "entre les lots."
        )

    else:
        st.info(
            f"La simulation dépasse l'objectif "
            f"de {euro(ecart)}."
        )
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Vente simulée HT",
        euro(vente_simulee),
    )

    col2.metric(
        "Marge brute simulée HT",
        euro(vente_simulee - total_achat),
    )

    col3.metric(
        "Écart avec l'objectif",
        euro(ecart),
    ) 

    st.divider()

    st.subheader("Détail des lots et bordereaux")

    for (numero, nom), lot in articles.groupby(
        ["Lot", "Nom du lot"],
        sort=False,
    ):

        achat_lot = lot["Total achat HT"].sum()
        vente_lot = lot["Total vente HT"].sum()

        with st.expander(
            f"Lot {numero} — {nom}"
        ):

            for nom_bordereau, bordereau in lot.groupby(
                "Bordereau",
                sort=False,
            ):

                st.markdown(
                    f"**Détail des articles — {nom_bordereau}**"
                )

                colonnes = [
                    "Désignation",
                    "Quantité",
                    "Prix achat unitaire",
                    "Total achat HT",
                    "Total vente HT",
                ]

                st.dataframe(
                    bordereau[colonnes],
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "Prix achat unitaire": st.column_config.NumberColumn(
                            "PU achat HT",
                            format="%.2f €",
                        ),
                        "Total achat HT": st.column_config.NumberColumn(
                            "Total achat HT",
                            format="%.2f €",
                        ),
                        "Total vente HT": st.column_config.NumberColumn(
                            "Total vente HT",
                            format="%.2f €",
                        ),
                    },
                )

            col1, col2 = st.columns(2)

            col1.metric(
                "Achat du lot",
                euro(achat_lot),
            )

            col2.metric(
                "Vente du lot",
                euro(vente_lot),
            )

    st.divider()

    st.subheader("Récapitulatif par lot")

    resume = (
        articles.groupby(
            ["Lot", "Nom du lot"],
            sort=False,
        )[
            [
                "Total achat HT",
                "Total vente HT",
            ]
        ]
        .sum()
        .reset_index()
    )

    resume["Marge %"] = resume["Lot"].map(
        marges_lots
    )

    resume_affichage = resume.copy()

    resume_affichage["Total achat HT"] = (
        resume_affichage["Total achat HT"].apply(euro)
    )

    resume_affichage["Total vente HT"] = (
        resume_affichage["Total vente HT"].apply(euro)
    )

    st.dataframe(
        resume_affichage,
        hide_index=True,
        width="stretch",
        column_config={
            "Marge %": st.column_config.NumberColumn(
                "Marge %",
                format="%.1f %%",
            ),
        },
    )

    st.divider()

    st.subheader("Récapitulatif final")
    col1, col2 = st.columns(2)
    col1.metric(
        "Prix Achat HT",
        euro(total_achat),
    )

    col2.metric(
        "Prix vente HT",
        euro(vente_simulee),
    )

    col1, col2 = st.columns(2)
    
    col1.metric(
        "Marge brute HT",
        euro(vente_simulee - total_achat),
    )

    col2.metric(
        "Écart avec l'objectif",
        euro(ecart),
    ) 
