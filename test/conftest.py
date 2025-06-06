import networkx as nx
import pytest
import pandas as pd

from snomed_graphe.graphe import SnomedGraph
from typing import Dict, List, Tuple, Union


@pytest.fixture
def concept_file() -> pd.DataFrame:
    return pd.DataFrame({"id": ["1009", "2009", "3009", "4009"], "active": ["1", "1", "0", "1"]})


@pytest.fixture
def desc_en_file() -> pd.DataFrame:
    return pd.DataFrame({
        "id": ["1019", "2019", "3019", "4019", "5019", "6019", "7019", "8019", "9019", "10019",
               "11019"],
        "active": ["1", "1", "1", "1", "1", "0", "1", "1", "1", "1", "1"],
        "conceptId": ["1009", "1009", "1009", "1009", "1009", "1009", "3009", "2009", "2009",
                      "4009", "4009"],
        "languageCode": ["en", "en", "en", "en", "en", "en", "en", "en", "en", "en", "en"],
        "typeId": ["900000000000003001", "900000000000013009", "900000000000013009",
                   "900000000000013009", "900000000000013009", "900000000000013009",
                   "900000000000003001", "900000000000003001", "900000000000013009",
                   "900000000000003001", "900000000000013009"],
        "term": ["Toe structure (body structure)", "Toe structure US", "Toe structure GB",
                 "Toe", "Digit of foot", "Finger of foot", "Toe structure (environment)",
                 "Myocardial infarction (disorder)", "Myocardial infarction", "Is a (attribute)",
                 "Is a"]
    })


@pytest.fixture
def desc_fr_file() -> pd.DataFrame:
    return pd.DataFrame({
        "id": ["12019", "13019"],
        "active": ["1", "1"],
        "conceptId": ["2009", "2009"],
        "languageCode": ["fr", "fr"],
        "typeId": ["900000000000013009", "900000000000013009"],
        "term": ["crise cardiaque", "infarctus du myocarde"]
    })


@pytest.fixture
def desc() -> pd.DataFrame:
    return pd.DataFrame({
        "id": ["12019", "5019", "13019", "11019", "10019", "9019", "8019", "4019", "1019", "3019",
               "2019"],
        "active": ["1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"],
        "conceptId": ["2009", "1009", "2009", "4009", "4009", "2009", "2009", "1009", "1009",
                      "1009", "1009"],
        "languageCode": ["fr", "en", "fr", "en", "en", "en", "en", "en", "en", "en", "en"],
        "typeId": ["900000000000013009", "900000000000013009", "900000000000013009",
                   "900000000000013009", "900000000000003001", "900000000000013009",
                   "900000000000003001", "900000000000013009", "900000000000003001",
                   "900000000000013009", "900000000000013009"],
        "term": ["crise cardiaque", "Digit of foot", "infarctus du myocarde", "Is a",
                 "Is a (attribute)", "Myocardial infarction", "Myocardial infarction (disorder)",
                 "Toe", "Toe structure (body structure)", "Toe structure GB", "Toe structure US",]
    })


@pytest.fixture
def en_accept_file() -> pd.DataFrame:
    return pd.DataFrame({
        "active": ["1", "1", "1", "1", "1", "0", "0", "1", "1", "1", "1"],
        "refsetId": ["900000000000509007", "900000000000509007", "900000000000508004",
                     "900000000000509007", "900000000000509007", "900000000000509007",
                     "900000000000509007", "900000000000509007", "900000000000509007",
                     "900000000000509007", "900000000000509007"],
        "referencedComponentId": ["1019", "2019", "3019", "4019", "5019", "6019", "7019", "8019",
                                  "9019", "10019", "11019"],
        "acceptabilityId": ["900000000000548007", "900000000000548007", "900000000000548007",
                            "900000000000549004", "900000000000549004", "900000000000549004",
                            "900000000000548007", "900000000000548007", "900000000000548007",
                            "900000000000548007", "900000000000548007"]
    })


@pytest.fixture
def fr_accept_file() -> pd.DataFrame:
    return pd.DataFrame({
        "active": ["1", "1"],
        "refsetId": ["10031000315102", "10031000315102"],
        "referencedComponentId": ["12019", "13019"],
        "acceptabilityId": ["900000000000548007", "900000000000549004"]
    })


@pytest.fixture
def desc_accept() -> pd.DataFrame:
    return pd.DataFrame({
        "conceptId": ["2009", "1009", "2009", "4009", "4009", "2009", "2009", "1009", "1009",
                      "1009"],
        "languageCode": ["fr", "en", "fr", "en", "en", "en", "en", "en", "en", "en"],
        "typeId": ["900000000000013009", "900000000000013009", "900000000000013009",
                   "900000000000013009", "900000000000003001", "900000000000013009",
                   "900000000000003001", "900000000000013009", "900000000000003001",
                   "900000000000013009"],
        "term": ["crise cardiaque", "Digit of foot", "infarctus du myocarde", "Is a",
                 "Is a (attribute)", "Myocardial infarction", "Myocardial infarction (disorder)",
                 "Toe", "Toe structure (body structure)", "Toe structure US"],
        "acceptabilityId": ["900000000000548007", "900000000000549004", "900000000000549004",
                            "900000000000548007", "900000000000548007", "900000000000548007",
                            "900000000000548007", "900000000000549004", "900000000000548007",
                            "900000000000548007"]
    })


@pytest.fixture
def relationship_file() -> pd.DataFrame:
    return pd.DataFrame({
        "active": ["1", "0"],
        "sourceId": ["1009", "1009"],
        "destinationId": ["2009", "2009"],
        "relationshipGroup": ["0", "1"],
        "typeId": ["4009", "4009"]
    })


@pytest.fixture
def rel() -> pd.DataFrame:
    return pd.DataFrame({"active": ["1"], "src": ["1009"], "tgt": ["2009"], "group": ["0"],
                         "attribute": ["4009"]})


@pytest.fixture
def nodes() -> pd.DataFrame:
    df = pd.DataFrame({
        "conceptId": ["4009", "2009", "1009"],
        "fsn": ["Is a (attribute)", "Myocardial infarction (disorder)",
                "Toe structure (body structure)"],
        "pt_en": ["Is a", "Myocardial infarction", "Toe structure US"],
        "pt_lang": ["", "crise cardiaque", ""],
        "syn_en": ["", "", ["Digit of foot", "Toe"]],
        "syn_lang": ["", ["infarctus du myocarde"], ""]
    })
    df.set_index("conceptId", inplace=True)

    return df


@pytest.fixture
def sct() -> SnomedGraph:
    nodes = pd.DataFrame({
        "conceptId": ["129574000", "1163440003", "311796008", "311792005", "311793000",
                      "116680003", "363698007", "116676008", "255234002", "263502005", "74281007",
                      "55641003", "387713003", "55470003", "424124008", "58148009", "6975006",
                      "404684003", "900000000000441003", "123037004", "71388002", "362981000",
                      "138875005", "test"],
        "fsn": ["Postoperative myocardial infarction (disorder)",
                "Postoperative acute myocardial infarction (disorder)",
                "Postoperative subendocardial myocardial infarction (disorder)",
                "Postoperative transmural myocardial infarction of anterior wall (disorder)",
                "Postoperative transmural myocardial infarction of inferior wall (disorder)",
                "Is a (attribute)", "Finding site (attribute)",
                "Associated morphology (attribute)", "After (attribute)",
                "Clinical course (attribute)", "Myocardium structure (body structure)",
                "Infarct (morphologic abnormality)", "Surgical procedure (procedure)",
                "Acute infarct (morphologic abnormality)",
                "Sudden onset AND/OR short duration (qualifier value)",
                "Structure of subendocardial myocardium (body structure)",
                "Structure of anterior myocardium (body structure)", "Clinical finding (finding)",
                "SNOMED CT Model Component (metadata)", "Body structure (body structure)",
                "Procedure (procedure)", "Qualifier value (qualifier value)",
                "SNOMED CT Concept (SNOMED RT+CTV3)", "Test (test)"],
        "pt_en": ["Postoperative myocardial infarction",
                  "Postoperative acute myocardial Infarction",
                  "Postoperative subendocardial myocardial infarction",
                  "Postoperative transmural myocardial infarction of anterior wall",
                  "Postoperative transmural myocardial infarction of inferior wall", "Is a",
                  "Finding site", "Associated morphology", "After", "Clinical course",
                  "Myocardium structure", "Infarct", "Surgical procedure", "Acute infarct",
                  "Sudden onset AND/OR short duration", "Structure of subendocardial myocardium",
                  "Structure of anterior myocardium", "Clinical finding",
                  "SNOMED CT Model Component", "Body structure", "Procedure", "Qualifier value",
                  "SNOMED CT concept", "Test"],
        "pt_lang": ["infarctus myocardique postoperatoire",
                    "infarctus du myocarde aigu postoperatoire",
                    "infarctus myocardique sous-endocardique postoperatoire",
                    "infarctus myocardique transmural anterieur postoperatoire",
                    "infarctus myocardique transmural inferieur postoperatoire", "est un(e)",
                    "localisation de constatation", "morphologie associee", "",
                    "evolution clinique", "myocarde", "infarctus", "intervention chirurgicale", "",
                    "apparition soudaine ou de courte duree", "myocarde sous-endocardique",
                    "myocarde anterieur", "constatation clinique", "", "structure corporelle",
                    "procedure", "valeur de l'attribut", "concept SNOMED CT", ""],
        "syn_en": ["", ["Acute myocardial infarction following operative procedure"], "", "", "",
                   "", "", ["Morphology"], ["Following"], "", ["Cardiac muscle", "Myocardium"],
                   ["Infarction"], ["Operation", "Operative procedure", "Surgery"],
                   ["Recent infarct"], "", ["Subendocardial myocardium"], ["Anterior myocardium"],
                   "", "", ["Body structures"], "", "", "", ""],
        "syn_lang": ["", ["IDM (infarctus du myocarde) aigu postoperatoire"], "", "", "", "", "",
                     "", "", "", ["myocardium", "structure du myocarde", "structure myocardique"],
                     "", "", "", "", "",
                     ["paroi anterieure du myocarde", "structure du myocarde anterieur"], "", "",
                     "", ["intervention"], "", "", ""]
    })
    nodes.set_index("conceptId", inplace=True)
    rel = pd.DataFrame({
        "active": ["1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
                   "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
                   "1", "1", "1", "1", "1", "1", "1", "1"],
        "src": ["1163440003", "311796008", "311792005", "311793000", "116680003", "363698007",
                "116676008", "255234002", "263502005", "74281007", "55641003", "55470003",
                "58148009", "6975006", "387713003", "424124008", "129574000", "404684003",
                "900000000000441003", "123037004", "71388002", "362981000", "test", "test",
                "129574000", "1163440003", "311796008", "311792005", "311793000", "129574000",
                "1163440003", "311796008", "311792005", "311793000", "129574000", "1163440003",
                "311796008", "311792005", "311793000", "1163440003"],
        "tgt": ["129574000", "129574000", "129574000", "129574000", "900000000000441003",
                "900000000000441003", "900000000000441003", "900000000000441003",
                "900000000000441003", "123037004", "123037004", "123037004", "123037004",
                "123037004", "71388002", "362981000", "404684003", "138875005", "138875005",
                "138875005", "138875005", "138875005", "311793000", "116680003", "74281007",
                "74281007", "58148009", "6975006", "74281007", "55641003", "55470003", "55641003",
                "55641003", "55641003", "387713003", "387713003", "387713003", "387713003",
                "387713003", "424124008"],
        "group": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
                  "0", "0", "0", "0", "0", "0", "0", "0", "1", "1", "1", "1", "1", "1", "1", "1",
                  "1", "1", "2", "2", "2", "2", "2", "3"],
        "attribute": ["116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "363698007", "363698007", "363698007", "363698007", "363698007", "116676008",
                      "116676008", "116676008", "116676008", "116676008", "255234002", "255234002",
                      "255234002", "255234002", "255234002", "263502005"]
    })

    g = nx.from_pandas_edgelist(rel, source="src", target="tgt",
                                edge_attr=["src", "tgt", "group", "attribute"],
                                create_using=nx.DiGraph)
    g.add_nodes_from((id, dict(row)) for id, row in nodes.iterrows())

    return SnomedGraph(g, lang="fr")


@pytest.fixture
def in_rel() -> List[Tuple[str]]:
    return [('1163440003', '116680003', '129574000'),
            ('311796008', '116680003', '129574000'),
            ('311792005', '116680003', '129574000'),
            ('311793000', '116680003', '129574000')]


@pytest.fixture
def out_rel() -> List[Tuple[str]]:
    return [('129574000', '116680003', '404684003'),
            ('129574000', '363698007', '74281007'),
            ('129574000', '116676008', '55641003'),
            ('129574000', '255234002', '387713003')]


@pytest.fixture
def details() -> Dict[str, str]:
    return {
        "fsn": "Postoperative myocardial infarction (disorder)",
        "pt_en": "Postoperative myocardial infarction",
        "pt_lang": "infarctus myocardique postoperatoire",
        "sctid": "129574000",
        "semtag": "disorder",
        "syn_en": "",
        "syn_lang": ""
    }


@pytest.fixture
def full() -> Dict[str, Union[str, Dict]]:
    return {
        "children": ["1163440003", "311796008", "311792005", "311793000"],
        "fsn": "Postoperative myocardial infarction (disorder)",
        "lang": "fr",
        "parents": ["404684003"],
        "pt_en": "Postoperative myocardial infarction",
        "pt_lang": "infarctus myocardique postoperatoire",
        "relationships": {
            "1": [("363698007", "74281007"), ("116676008", "55641003")],
            "2": [("255234002", "387713003")]
        },
        "sctid": "129574000",
        "semtag": "disorder",
        "syn_en": "",
        "syn_lang": ""
    }


@pytest.fixture
def grouped_rel() -> Dict[str, List[Tuple[str]]]:
    return {
        "1": [('363698007', '74281007'), ('116676008', '55641003')],
        "2": [('255234002', '387713003')]
    }


@pytest.fixture
def ungrouped_rel() -> List[Tuple[str]]:
    return [('363698007', '74281007'), ('116676008', '55641003'), ('255234002', '387713003')]


@pytest.fixture
def ancestors() -> List[str]:
    return ["138875005", "404684003"]


@pytest.fixture
def children() -> List[str]:
    return ["1163440003", "311792005", "311793000", "311796008"]


@pytest.fixture
def descendants() -> List[str]:
    return ["1163440003", "311792005", "311793000", "311796008", "test"]


@pytest.fixture
def neighbors() -> List[str]:
    return ["1163440003", "116680003", "123037004", "129574000", "138875005", "311792005",
            "311793000", "311796008", "362981000", "404684003", "71388002", "900000000000441003",
            "test"]


@pytest.fixture
def parents() -> List[str]:
    return ["404684003"]


@pytest.fixture
def hierarchical_path() -> List[str]:
    return ["test", "116680003", "900000000000441003", "138875005"]


@pytest.fixture
def path() -> List[str]:
    return ["1163440003", "424124008", "362981000"]


@pytest.fixture
def df_nodes() -> pd.DataFrame:
    nodes = pd.DataFrame({
        "sctid": ["1163440003", "129574000", "311796008", "311792005", "311793000", "116680003",
                  "900000000000441003", "363698007", "116676008", "255234002", "263502005",
                  "74281007", "123037004", "55641003", "55470003", "58148009", "6975006",
                  "387713003", "71388002", "424124008", "362981000", "404684003", "138875005",
                  "test"],
        "fsn": ["Postoperative acute myocardial infarction (disorder)",
                "Postoperative myocardial infarction (disorder)",
                "Postoperative subendocardial myocardial infarction (disorder)",
                "Postoperative transmural myocardial infarction of anterior wall (disorder)",
                "Postoperative transmural myocardial infarction of inferior wall (disorder)",
                "Is a (attribute)", "SNOMED CT Model Component (metadata)",
                "Finding site (attribute)", "Associated morphology (attribute)",
                "After (attribute)", "Clinical course (attribute)",
                "Myocardium structure (body structure)", "Body structure (body structure)",
                "Infarct (morphologic abnormality)", "Acute infarct (morphologic abnormality)",
                "Structure of subendocardial myocardium (body structure)",
                "Structure of anterior myocardium (body structure)",
                "Surgical procedure (procedure)", "Procedure (procedure)",
                "Sudden onset AND/OR short duration (qualifier value)",
                "Qualifier value (qualifier value)", "Clinical finding (finding)",
                "SNOMED CT Concept (SNOMED RT+CTV3)", "Test (test)"],
        "pt_en": ["Postoperative acute myocardial Infarction",
                  "Postoperative myocardial infarction",
                  "Postoperative subendocardial myocardial infarction",
                  "Postoperative transmural myocardial infarction of anterior wall",
                  "Postoperative transmural myocardial infarction of inferior wall", "Is a",
                  "SNOMED CT Model Component", "Finding site", "Associated morphology", "After",
                  "Clinical course", "Myocardium structure", "Body structure", "Infarct",
                  "Acute infarct", "Structure of subendocardial myocardium",
                  "Structure of anterior myocardium", "Surgical procedure", "Procedure",
                  "Sudden onset AND/OR short duration", "Qualifier value", "Clinical finding",
                  "SNOMED CT concept", "Test"],
        "pt_lang": ["infarctus du myocarde aigu postoperatoire",
                    "infarctus myocardique postoperatoire",
                    "infarctus myocardique sous-endocardique postoperatoire",
                    "infarctus myocardique transmural anterieur postoperatoire",
                    "infarctus myocardique transmural inferieur postoperatoire",
                    "est un(e)", "", "localisation de constatation", "morphologie associee", "",
                    "evolution clinique", "myocarde", "structure corporelle", "infarctus", "",
                    "myocarde sous-endocardique", "myocarde anterieur",
                    "intervention chirurgicale", "procedure",
                    "apparition soudaine ou de courte duree", "valeur de l'attribut",
                    "constatation clinique", "concept SNOMED CT", ""],
        "syn_en": [["Acute myocardial infarction following operative procedure"], "", "", "", "",
                   "", "", "", ["Morphology"], ["Following"], "", ["Cardiac muscle", "Myocardium"],
                   ["Body structures"], ["Infarction"], ["Recent infarct"],
                   ["Subendocardial myocardium"], ["Anterior myocardium"],
                   ["Operation", "Operative procedure", "Surgery"], "", "", "", "", "", ""],
        "syn_lang": [["IDM (infarctus du myocarde) aigu postoperatoire"], "", "", "", "", "", "",
                     "", "", "", "",
                     ["myocardium", "structure du myocarde", "structure myocardique"], "", "", "",
                     "", ["paroi anterieure du myocarde", "structure du myocarde anterieur"], "",
                     ["intervention"], "", "", "", "", ""]
    })
    nodes.set_index("sctid", inplace=True)

    return nodes


@pytest.fixture
def df_edges() -> pd.DataFrame:
    edges = pd.DataFrame({
        "source": ["1163440003", "1163440003", "1163440003", "1163440003", "1163440003",
                   "129574000", "129574000", "129574000", "129574000", "311796008", "311796008",
                   "311796008", "311796008", "311792005", "311792005", "311792005", "311792005",
                   "311793000", "311793000", "311793000", "311793000", "116680003",
                   "900000000000441003", "363698007", "116676008", "255234002", "263502005",
                   "74281007", "123037004", "55641003", "55470003", "58148009", "6975006",
                   "387713003", "71388002", "424124008", "362981000", "404684003", "test", "test"],
        "target": ["129574000", "74281007", "55470003", "387713003", "424124008", "404684003",
                   "74281007", "55641003", "387713003", "129574000", "58148009", "55641003",
                   "387713003", "129574000", "6975006", "55641003", "387713003", "129574000",
                   "74281007", "55641003", "387713003", "900000000000441003", "138875005",
                   "900000000000441003", "900000000000441003", "900000000000441003",
                   "900000000000441003", "123037004", "138875005", "123037004", "123037004",
                   "123037004", "123037004", "71388002", "138875005", "362981000", "138875005",
                   "138875005", "311793000", "116680003"],
        "group": ["0", "1", "1", "2", "3", "0", "1", "1", "2", "0", "1", "1", "2", "0", "1", "1",
                  "2", "0", "1", "1", "2", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
                  "0", "0", "0", "0", "0", "0", "0", "0"],
        "src": ["1163440003", "1163440003", "1163440003", "1163440003", "1163440003", "129574000",
                "129574000", "129574000", "129574000", "311796008", "311796008", "311796008",
                "311796008", "311792005", "311792005", "311792005", "311792005", "311793000",
                "311793000", "311793000", "311793000", "116680003", "900000000000441003",
                "363698007", "116676008", "255234002", "263502005", "74281007", "123037004",
                "55641003", "55470003", "58148009", "6975006", "387713003", "71388002",
                "424124008", "362981000", "404684003", "test", "test"],
        "attribute": ["116680003", "363698007", "116676008", "255234002", "263502005", "116680003",
                      "363698007", "116676008", "255234002", "116680003", "363698007", "116676008",
                      "255234002", "116680003", "363698007", "116676008", "255234002", "116680003",
                      "363698007", "116676008", "255234002", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "116680003"],
        "tgt": ["129574000", "74281007", "55470003", "387713003", "424124008", "404684003",
                "74281007", "55641003", "387713003", "129574000", "58148009", "55641003",
                "387713003", "129574000", "6975006", "55641003", "387713003", "129574000",
                "74281007", "55641003", "387713003", "900000000000441003", "138875005",
                "900000000000441003", "900000000000441003", "900000000000441003",
                "900000000000441003", "123037004", "138875005", "123037004", "123037004",
                "123037004", "123037004", "71388002", "138875005", "362981000", "138875005",
                "138875005", "311793000", "116680003"]
    })

    return edges


@pytest.fixture
def sub_sct() -> SnomedGraph:
    nodes = pd.DataFrame({
        "conceptId": ["129574000", "311793000", "116680003", "363698007", "116676008",
                      "255234002", "74281007", "55641003", "387713003", "404684003",
                      "900000000000441003", "123037004", "71388002", "138875005", "test"],
        "fsn": ["Postoperative myocardial infarction (disorder)",
                "Postoperative transmural myocardial infarction of inferior wall (disorder)",
                "Is a (attribute)", "Finding site (attribute)",
                "Associated morphology (attribute)", "After (attribute)",
                "Myocardium structure (body structure)", "Infarct (morphologic abnormality)",
                "Surgical procedure (procedure)", "Clinical finding (finding)",
                "SNOMED CT Model Component (metadata)", "Body structure (body structure)",
                "Procedure (procedure)", "SNOMED CT Concept (SNOMED RT+CTV3)", "Test (test)"],
        "pt_en": ["Postoperative myocardial infarction",
                  "Postoperative transmural myocardial infarction of inferior wall", "Is a",
                  "Finding site", "Associated morphology", "After", "Myocardium structure",
                  "Infarct", "Surgical procedure", "Clinical finding", "SNOMED CT Model Component",
                  "Body structure", "Procedure", "SNOMED CT concept", "Test"],
        "pt_lang": ["infarctus myocardique postoperatoire",
                    "infarctus myocardique transmural inferieur postoperatoire", "est un(e)",
                    "localisation de constatation", "morphologie associee", "", "myocarde",
                    "infarctus", "intervention chirurgicale", "constatation clinique", "",
                    "structure corporelle", "procedure", "concept SNOMED CT", ""],
        "syn_en": ["", "", "", "", ["Morphology"], ["Following"], ["Cardiac muscle", "Myocardium"],
                   ["Infarction"], ["Operation", "Operative procedure", "Surgery"], "", "",
                   ["Body structures"], "", "", ""],
        "syn_lang": ["", "", "", "", "", "",
                     ["myocardium", "structure du myocarde", "structure myocardique"], "", "", "",
                     "", "", ["intervention"], "", ""]
    })
    nodes.set_index("conceptId", inplace=True)
    rel = pd.DataFrame({
        "active": ["1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
                   "1", "1", "1", "1", "1"],
        "src": ["311793000", "116680003", "363698007", "116676008", "255234002", "74281007",
                "55641003", "387713003", "129574000", "404684003", "900000000000441003",
                "123037004", "71388002", "test", "test", "129574000", "311793000", "129574000",
                "311793000", "129574000", "311793000"],
        "tgt": ["129574000", "900000000000441003", "900000000000441003", "900000000000441003",
                "900000000000441003", "123037004", "123037004", "71388002", "404684003",
                "138875005", "138875005", "138875005", "138875005", "311793000", "116680003",
                "74281007", "74281007", "55641003", "55641003", "387713003", "387713003"],
        "group": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "1",
                  "1", "1", "1", "2", "2"],
        "attribute": ["116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "116680003", "116680003", "116680003",
                      "116680003", "116680003", "116680003", "363698007", "363698007", "116676008",
                      "116676008", "255234002", "255234002"]
    })

    g = nx.from_pandas_edgelist(rel, source="src", target="tgt",
                                edge_attr=["src", "tgt", "group", "attribute"],
                                create_using=nx.DiGraph)
    g.add_nodes_from((id, dict(row)) for id, row in nodes.iterrows())

    return SnomedGraph(g, lang="fr")
