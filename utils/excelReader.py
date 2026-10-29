from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

import pandas as pd


def nettoyer_excel(contenu):
    """Retire l'attribut non standard isReadOnly des noms définis."""

    entree = BytesIO(contenu)
    sortie = BytesIO()

    with ZipFile(entree, "r") as source:
        with ZipFile(sortie, "w") as destination:

            for fichier in source.infolist():

                donnees = source.read(fichier.filename)

                if fichier.filename == "xl/workbook.xml":

                    racine = ET.fromstring(donnees)

                    namespace = (
                        "{http://schemas.openxmlformats.org/"
                        "spreadsheetml/2006/main}"
                    )

                    for element in racine.iter(
                        f"{namespace}definedName"
                    ):
                        element.attrib.pop("isReadOnly", None)

                    donnees = ET.tostring(
                        racine,
                        encoding="utf-8",
                        xml_declaration=True,
                    )

                destination.writestr(fichier, donnees)

    sortie.seek(0)
    return sortie


def readExcel(fichier):
    """Charge un fichier Excel après nettoyage."""

    contenu = fichier.getvalue()

    excel_nettoye = nettoyer_excel(contenu)

    return pd.read_excel(
        excel_nettoye,
        engine="openpyxl",
    )
