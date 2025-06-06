import networkx as nx
import os.path as op
import pandas as pd

from datetime import datetime
from snomed_graphe.graphe import SnomedGraph
from tqdm import tqdm
from typing import Tuple

#####################
# Méthodes internes #
#####################


def _get_nodes_details(desc: pd.DataFrame, lang: str) -> pd.DataFrame:
    """
    Création d'un DataFrame contenant les attributs des nœuds

    Args:
        desc: DataFrame contenant des descriptions.
        lang: Autre langue que l'anglais présente dans la release, par défaut 'fr'.

    Returns:
        Un DataFrame contenant les FSN, les PT et les SYN en anglais et dans une autre langue.
    """
    # Division des descriptions par langue et acceptabilité
    pt_en = desc.loc[(desc.loc[:, "typeId"] != "900000000000003001")
                     & (desc.loc[:, "acceptabilityId"] == "900000000000548007")
                     & (desc.loc[:, "languageCode"] == "en")]
    syn_en = desc.loc[(desc.loc[:, "acceptabilityId"] == "900000000000549004")
                      & (desc.loc[:, "languageCode"] == "en")]
    if lang:
        pt_lang = desc.loc[(desc.loc[:, "typeId"] != "900000000000003001")
                           & (desc.loc[:, "acceptabilityId"] == "900000000000548007")
                           & (desc.loc[:, "languageCode"] == lang)]
        syn_lang = desc.loc[(desc.loc[:, "acceptabilityId"] == "900000000000549004")
                            & (desc.loc[:, "languageCode"] == lang)]

    # Initialisation du DataFrame des nœuds
    nodes = desc.loc[(desc.loc[:, "typeId"] == "900000000000003001")
                     & (desc.loc[:, "languageCode"] == "en"), ["conceptId", "term"]]
    nodes.set_index("conceptId", inplace=True)

    # Ajout des colonnes pour termes préférés (PT)
    nodes = pd.concat([nodes, pt_en.groupby("conceptId")["term"].apply(list)], axis=1)
    if lang:
        nodes = pd.concat([nodes, pt_lang.groupby("conceptId")["term"].apply(list)], axis=1)
    # Ajout des colonnes pour synonymes acceptables (SYN)
    nodes = pd.concat([nodes, syn_en.groupby("conceptId")["term"].apply(list)], axis=1)
    if lang:
        nodes = pd.concat([nodes, syn_lang.groupby("conceptId")["term"].apply(list)], axis=1)

    # Normalisation du DataFrame
    nodes.fillna("", inplace=True)
    nodes.columns = ["fsn", "pt_en", "pt_lang", "syn_en", "syn_lang"]
    nodes.loc[:, "pt_en"] = ["".join(map(str, col)) for col in nodes.loc[:, "pt_en"]]
    nodes.loc[:, "pt_lang"] = ["".join(map(str, col)) for col in nodes.loc[:, "pt_lang"]]

    return nodes


def _get_descriptions(concepts_path: str, en_desc_path: str, lang_desc_path: str,
                      lang: str = "fr") -> pd.DataFrame:
    """
    Renvoie un DataFrame contenant les informations sur les descriptions.

    Args:
        concepts_path: Chemin vers le fichier des concepts
        en_desc_path: Chemin vers le fichier des descriptions anglaises
        lang_desc_path: Chemin vers le fichier des descriptions non anglaises
        lang: Autre langue que l'anglais présente dans la release, par défaut 'fr'.

    Returns:
        DataFrame contenant les descriptions.
    """
    # Charge les concepts
    print("Lecture des concepts ...")
    concepts = pd.read_csv(concepts_path, sep="\t", dtype=str, usecols=["id", "active"])
    concepts = concepts.loc[concepts.loc[:, "active"] == "1"]

    # Charge les descriptions
    print("Lecture des descriptions en ...")
    desc = pd.read_csv(en_desc_path, sep="\t", dtype=str, quoting=3,
                       encoding="UTF-8", na_filter=False,
                       usecols=["id", "active", "conceptId", "languageCode", "typeId", "term"])
    if lang:
        print(f"Lecture des descriptions {lang} ...")
        desc = pd.concat([
            desc,
            pd.read_csv(lang_desc_path, sep="\t", dtype=str, quoting=3,
                        encoding="UTF-8", na_filter=False,
                        usecols=["id", "active", "conceptId", "languageCode", "typeId", "term"])
        ])
    desc = desc.loc[desc.loc[:, "active"] == "1"]

    # Supprime les descriptions actives de concepts inactifs
    desc = desc.loc[desc.loc[:, "conceptId"].isin(concepts.loc[:, "id"])]

    # Trier et réindexer
    desc = desc.iloc[desc.loc[:, "term"].str.lower().argsort()]
    desc.reset_index(drop=True, inplace=True)

    return desc


def _get_relations(path: str) -> pd.DataFrame:
    """
    Renvoie un DataFrame contenant les informations sur les relations.

    Args:
        path: Chemin vers le fichier des relations.

    Returns:
        DataFrame contenant les relations.
    """
    # Charge les relations
    print("Lecture des relations ...")
    rs = pd.read_csv(path, sep="\t", dtype=str, usecols=[
        "active", "sourceId", "destinationId", "relationshipGroup", "typeId"])
    rs = rs.loc[rs.loc[:, "active"] == "1"]
    rs.columns = ["active", "src", "tgt", "group", "attribute"]

    return rs


def _rf2_paths(path: str, lang: str = "fr") -> Tuple[str]:
    """
    Génère les chemins vers les fichiers d'intérêts au sein d'une archive RF2.

    Args:
        path: Chemin vers l'archive RF2.
        lang: Autre langue que l'anglais présente dans la release, par défaut 'fr'.

    Returns:
        Un Tuple contenant les fichiers de concepts, descriptions, relations et refset
        de langue.
    """
    # Normaliser le chemin de l'archive RF2
    path = op.abspath(path)
    # Vérification de l'existance du dossier
    if not op.exists(path):
        raise AssertionError(f"Le chemin '{path}' n'existe pas")

    try:
        # Récupération des différents éléments à partir du nom du dossier
        elements = op.basename(path).split("_")
        if len(elements) == 5:
            _, _, _, ns, date = elements
        elif len(elements) == 4:
            _, _, _, date = elements
            ns = "INT"
        else:
            raise AttributeError
        date = datetime.strptime(date, "%Y%m%dT%H%M%SZ").strftime("%Y%m%d")
    except (AttributeError, ValueError, AssertionError):
        raise AssertionError(f"Le dossier '{path}' ne suit pas les convention de nommage RF2.")

    terminology = op.join(path, "Snapshot/Terminology")
    language = op.join(path, "Snapshot/Refset/Language")

    # Création et vérification de l'existence du fichier des concepts
    concepts = op.join(terminology, f"sct2_Concept_Snapshot_{ns}_{date}.txt")
    if not op.exists(concepts):
        raise AssertionError(f"Le chemin '{concepts}' n'existe pas")

    # Création et vérification de l'existence du fichier des descriptions anglaises
    en_desc = op.join(terminology, f"sct2_Description_Snapshot-en_{ns}_{date}.txt")
    if not op.exists(en_desc):
        raise AssertionError(f"Le chemin '{en_desc}' n'existe pas")
    # Création et vérification de l'existence du refset de langue anglaise
    en_accept = op.join(language, f"der2_cRefset_LanguageSnapshot-en_{ns}_{date}.txt")
    if not op.exists(en_accept):
        raise AssertionError(f"Le chemin '{en_accept}' n'existe pas")

    if lang:
        # Création et vérification de l'existence du fichier des descriptions non anglaises
        lang_desc = op.join(terminology, f"sct2_Description_Snapshot-{lang}_{ns}_{date}.txt")
        if not op.exists(lang_desc):
            raise AssertionError(f"Le chemin '{lang_desc}' n'existe pas")
        # Création et vérification de l'existence du refset de langue non anglaise
        lang_accept = op.join(language, f"der2_cRefset_LanguageSnapshot-{lang}_{ns}_{date}.txt")
        if not op.exists(lang_accept):
            raise AssertionError(f"Le chemin '{lang_accept}' n'existe pas")
    else:
        # Pas de description non anglaise
        lang_desc = ""
        lang_accept = ""

    # Création et vérification de l'existence du fichier des relations
    relations = op.join(terminology, f"sct2_Relationship_Snapshot_{ns}_{date}.txt")
    if not op.exists(relations):
        raise AssertionError(f"Le chemin '{relations}' n'existe pas")

    return concepts, en_desc, en_accept, lang_desc, lang_accept, relations


def _set_acceptability(desc: pd.DataFrame, en_accept_path: str, lang_accept_path: str,
                       lang: str) -> pd.DataFrame:
    """
    Ajoute la valeur d'acceptabilité pour chaque description.

    Args:
        desc: DataFrame contenant les descriptions.
        en_accept_path: Chemin vers le refset de langue anglaise.
        lang_accept_path: Chemin vers le refset de langue non anglaise.
        lang: Autre langue que l'anglais présente dans la release, par défaut 'fr'.

    Returns:
        DataFrame contenant les descriptions et leur valeur d'acceptabilité.
    """
    # Charge les refsets de langue
    print("Lecture du refset de langue en ...")
    accept = pd.read_csv(
        en_accept_path, dtype=str, sep="\t",
        usecols=["active", "refsetId", "referencedComponentId", "acceptabilityId"]
    )

    if lang:
        print(f"Lecture du refset de langue {lang} ...")
        accept = pd.concat([
            accept,
            pd.read_csv(lang_accept_path, sep="\t", dtype=str,
                        usecols=["active", "refsetId", "referencedComponentId", "acceptabilityId"])
        ])

    accept = accept.loc[accept.loc[:, "active"] == "1"]

    # Supprimer les PT en anglais britannique des acceptabilités
    accept = accept.loc[(accept.loc[:, "refsetId"] != "900000000000508004")
                        | (accept.loc[:, "acceptabilityId"] != "900000000000548007")]

    # Ajouter l'acceptabilité aux descriptions
    desc = desc.merge(accept, how="left", left_on="id", right_on="referencedComponentId")

    # Supprimer les PT en anglais UK des descriptions
    desc.dropna(subset="acceptabilityId", inplace=True)
    # Supprimer les doublons entre anglais US & UK
    desc.drop(["id", "active_x", "active_y", "refsetId", "referencedComponentId"], axis=1,
              inplace=True)
    desc.drop_duplicates(inplace=True, ignore_index=True)

    return desc

#######################
# Méthodes de lecture #
#######################


def from_rf2(path: str, lang: str = "fr") -> SnomedGraph:
    """
    Crée un Graphe depuis une archive RF2.

    Args:
        path: Chemin vers l'archive RF2.
        lang: Autre langue que l'anglais présente dans la release, par défaut 'fr'.

    Returns:
        Un objet Graphe.
    """
    # Récupérer les chemins de chaque fichier d'intérêt
    c_path, en_path, en_accept_path, lang_path, lang_accept_path, rs_path = _rf2_paths(path)

    # Récupérer les descriptions
    desc = _get_descriptions(c_path, en_path, lang_path, lang)
    # Ajouter l'acceptabilité
    desc = _set_acceptability(desc, en_accept_path, lang_accept_path, lang)
    # Récupérer les relations
    relations = _get_relations(rs_path)

    # Création des arcs
    print("\nCréation des arcs ...")
    g = nx.from_pandas_edgelist(relations, source="src", target="tgt",
                                edge_attr=["src", "tgt", "group", "attribute"],
                                create_using=nx.DiGraph)

    # Rassemblement des attributs pour chaque nœuds
    nodes = _get_nodes_details(desc, lang)

    # Création des nœuds
    print("\nCréation des concepts ...")
    g.add_nodes_from((id, dict(row)) for id, row in tqdm(nodes.iterrows(), total=len(nodes)))

    # Retourne le graphe complet
    return SnomedGraph(g, lang=lang)


def from_serialized(path: str, lang: str = "fr") -> SnomedGraph:
    """
    Charge un graphe depuis une linéarisation.

    Args:
        path: Chemin + nom du fichier sauvegardé.
        lang: Langue autre que l'anglais utilisée dans le graphe.

    Returns:
        Un objet SnomedGraph.
    """
    g = nx.read_gml(path, destringizer=int)
    return SnomedGraph(g, lang=lang)

######################
# Méthode d'écriture #
######################


def save(g: SnomedGraph, path: str) -> None:
    """
    Sauvegarder un SnomedGraph au format gml.

    Args:
        g: Graphe SNOMED CT
        path: Chemin du fichier de sauvegarde
    """
    nx.write_gml(g.g, path)
