import pandas as pd
import networkx as nx
from tqdm import tqdm
from itertools import groupby
from itertools import pairwise
from typing import Any, Dict, Generator, List, Self, Set, Tuple
import os.path as op
from datetime import datetime
from snomed_graphe import concept as sct


class Graphe():
    """
    Une classe pour représenter une release SNOMED CT sous forme de graphe via NetworkX.
    """
    def __init__(self, g: nx.DiGraph, root: str = "138875005") -> None:
        """
        Crée une nouvelle instance de Graphe via un objet NetworkX DiGraph

        Args:
            g: Un DiGraph créé par Graphe.from_rf2() ou Graphe.from_serialized().
            root: SCTID du concept racine du Graphe
        """
        self.g = g
        self.root = root
        print(self)

    def __repr__(self) -> str:
        return f"{self.g.number_of_nodes()} concepts et {self.g.number_of_edges()} relations."

    def __iter__(self) -> Generator[Any, Any, None]:
        for sctid in self.g.nodes:
            yield self.get_concept_details(sctid)

    def __len__(self) -> int:
        return self.g.number_of_nodes()

    def __contains__(self, item) -> bool:
        return item in self.g

    def get_children(self, sctid: int) -> List[sct.ConceptDetails]:
        return [
            r.src for r in self.__get_in_relationships(sctid)
            if r.type_id == "116680003"
        ]

    def get_parents(self, sctid: int) -> List[sct.ConceptDetails]:
        return [
            r.tgt for r in self.__get_out_relationships(sctid)
            if r.type_id == "116680003"
        ]

    def get_inferred_relationships(self, sctid: int) -> List[sct.RelationshipGroup]:
        """
        Récupère les relations inferées d'un concept.
        (N.B. cela exclut les relations "is a" qui peuvent être récupérées par la
        fonction get_parents().)

        Args:
            sctid: Un identifiant de concept SNOMED CT.

        Returns:
            Une liste d'objets RelationshipGroup.
        """
        inferred_relationships = [
            r for r in self.__get_out_relationships(sctid)
            if r.type_id != "116680003"
        ]
        key_ = lambda r: r.group
        inferred_relationships_grouped = groupby(
            sorted(inferred_relationships, key=key_),
            key=key_
        )
        inferred_relationship_groups = [
            sct.RelationshipGroup(g, list(r))
            for g, r in inferred_relationships_grouped
        ]
        return inferred_relationship_groups

    def get_concept_details(self, sctid: int) -> sct.ConceptDetails:
        """
        Récupère les détails essentiels d'un concept : SCTID, FSN et synonymes.

        Args:
            sctid: Un identifiant de concept SNOMED CT valide.

        Returns:
            Un objet ConceptDetails.
        """
        return sct.ConceptDetails(sctid=sctid, **self.g.nodes[sctid])

    def get_full_concept(self, sctid: int) -> sct.Concept:
        """
        Récupère tous les détails d'un concept.

        Args:
            sctid: Un identifiant de concept SNOMED CT valide.

        Returns:
            Un objet Concept.
        """
        concept_details = self.get_concept_details(sctid)
        parents = self.get_parents(sctid)
        children = self.get_children(sctid)
        inferred_relationship_groups = self.get_inferred_relationships(sctid)
        return sct.Concept(concept_details, parents, children, inferred_relationship_groups)

    def __get_out_relationships(self, src_sctid: int) -> Generator[Dict, None, None]:
        src = sct.ConceptDetails(sctid=src_sctid, **self.g.nodes[src_sctid])
        for _, tgt_sctid in self.g.out_edges(src_sctid):
            tgt = sct.ConceptDetails(sctid=tgt_sctid, **self.g.nodes[tgt_sctid])
            vals = self.g.edges[(src_sctid, tgt_sctid)]
            yield sct.Relationship(src, tgt, **vals)

    def __get_in_relationships(self, tgt_sctid: int) -> Generator[Dict, None, None]:
        tgt = sct.ConceptDetails(sctid=tgt_sctid, **self.g.nodes[tgt_sctid])
        for src_sctid, _ in self.g.in_edges(tgt_sctid):
            src = sct.ConceptDetails(sctid=src_sctid, **self.g.nodes[src_sctid])
            vals = self.g.edges[(src_sctid, tgt_sctid)]
            yield sct.Relationship(src, tgt, **vals)

    def get_descendants(self, sctid: int, steps_removed: int = None) -> List[sct.ConceptDetails]:
        """
        Récupère les descendants d'un concept.

        Args:
            sctid: Un identifiant de concept SNOMED CT valide.
            steps_removed: Le nombre de niveaux de la hiérarchie jusqu'où descendre.
                           (1 => enfants; 2 => enfants + petit-enfants, etc)
                           si None alors tous les descendants sont récupérés.

        Returns:
            Une liste des SCTID des descendants.
        """
        if steps_removed is None:
            steps_removed = 99999
        elif steps_removed <= 0:
            raise AssertionError("steps_removed doit être > 0 ou None")
        children = self.get_children(sctid)
        descendants = set(children)
        if steps_removed > 1:
            for c in children:
                descendants = descendants.union(
                    self.get_descendants(c.sctid, steps_removed - 1)
                )
        return descendants

    def get_ancestors(self, sctid: int, steps_removed: int = None) -> List[sct.ConceptDetails]:
        """
        Récupère tous ancêtres d'un concept.

        Args:
            sctid: Un identifiant de concept SNOMED CT valide.
            steps_removed: Le nombre de niveaux de la hiérarchie jusqu'où remonter.
                           (1 => parents; 2 => parents + grand-parents, etc)
                           si None alors tous les parents sont récupérés.

        Returns:
            Une liste des SCTID de tous les ancêtres.
        """
        if steps_removed is None:
            steps_removed = 99999
        elif steps_removed <= 0:
            raise AssertionError("steps_removed doit être > 0 ou None")
        parents = self.get_parents(sctid)
        ancestors = set(parents)
        if steps_removed > 1:
            for p in parents:
                ancestors = ancestors.union(
                    self.get_ancestors(p.sctid, steps_removed - 1)
                )
        return set([a for a in ancestors if not a.sctid == self.root])

    def get_neighbourhood(self, sctid: int, steps_removed: int = 1) -> List[sct.ConceptDetails]:
        """
        Récupère les voisins d'un d'un concept.
        Les voisins comprennent les ancêtres, descendants et cousins jusqu'à un degré donné.

        Args:
            sctid: Un identifiant de concept SNOMED CT valide.
            steps_removed: Le nombre de niveaux jusqu'où descendre ou remonter dans la hiérarchie.
                           Par défaut à 1 (parents + enfants).

        Returns:
            Une liste contenant tous les SCTIDs des voisins.
        """
        assert steps_removed > 0
        parents = self.get_parents(sctid)
        children = self.get_children(sctid)
        neighbourhood = set(parents).union(children)
        if steps_removed > 1:
            for n in list(neighbourhood):
                neighbourhood = neighbourhood.union(
                    self.get_neighbourhood(n.sctid, steps_removed - 1)
                )
        neighbourhood = [
            n for n in neighbourhood
            if n.sctid not in [sctid, self.root]
        ]
        return neighbourhood

    def find_path(self, sctid1: int, sctid2: int, print_: bool = False) -> List[sct.Relationship]:
        """
        Retourne les détails du chemin le plus court existant entre 2 concepts.
        Le chemin prend en compte tous les attributs mais limite les resultats aux vrais ancêtres
        ou descentants - i.e. les concepts qui sont "cousins" l'un de l'autre ne seront pas dans
        le chemin retourné.

        Args:
            sctid1: Un identifiant de concept SNOMED CT valide.
            sctid2: Un identifiant de concept SNOMED CT valide.
            print_: Indique si le chemin est affiché ou non sous forme de string.

        Returns:
            Une liste de Relationship de la forme (source, attribut, cible).
            Ce sont les étapes du plus court chemin de la source à la cible.
        """
        path = []
        if nx.has_path(self.g, sctid1, sctid2):
            nodes = nx.shortest_path(self.g, sctid1, sctid2)
        elif nx.has_path(self.g, sctid2, sctid1):
            nodes = nx.shortest_path(self.g, sctid2, sctid1)
        else:
            nodes = []
        for src_sctid, tgt_sctid in pairwise(nodes):
            vals = self.g.edges[(src_sctid, tgt_sctid)]
            src = sct.ConceptDetails(sctid=src_sctid, **self.g.nodes[src_sctid])
            tgt = sct.ConceptDetails(sctid=tgt_sctid, **self.g.nodes[tgt_sctid])
            relationship = sct.Relationship(src, tgt, **vals)
            path.append(relationship)
        if print_:
            if len(nodes) > 0:
                str_ = f"[{path[0].src}]"
                for r in path:
                    str_ += f" ---[{r.type}]---> [{r.tgt}]"
                print(str_)
            else:
                print("No path found.")
        return path

    def path_to_root(self, sctid: int, print_: bool = False) -> List[sct.Relationship]:
        """
        Trouve le plus court chemin de relation "is a" d'un concept au concept racine.
        Peut être utilisé pour identifier la profondeur d'un concept.

        Args:
            sctid: Un identifiant de concept SNOMED CT valide.
            print_: Indique si le chemin est affiché ou non sous forme de string.
        Returns:
            Une liste de Relationship de la forme (source, attribut, cible).
            Ce sont les étapes du plus court chemin du concept à la racine.
        """
        shortest_path = None
        for nodes in nx.all_simple_paths(self.g, sctid, self.root):
            path = list()
            for src_sctid, tgt_sctid in pairwise(nodes):
                vals = self.g.edges[(src_sctid, tgt_sctid)]
                src = sct.ConceptDetails(sctid=src_sctid, **self.g.nodes[src_sctid])
                tgt = sct.ConceptDetails(sctid=tgt_sctid, **self.g.nodes[tgt_sctid])
                relationship = sct.Relationship(src, tgt, **vals)
                if relationship.type_id == self.is_a_relationship_typeId:
                    path.append(relationship)
                else:
                    path = None
                    break
            if path:
                if shortest_path:
                    if len(shortest_path) > len(path):
                        shortest_path = path
                else:
                    shortest_path = path
        if print_:
            str_ = f"[{shortest_path[0].src}]"
            for r in shortest_path:
                str_ += f" ---[{r.type}]---> [{r.tgt}]"
            print(str_)
        return shortest_path

    def save(self, path: str) -> None:
        """
        Sauvegarde ce Graphe

        Args:
            path: Chemin + nom du fichier où sauvegarder.
        """
        nx.write_gml(self.g, path)

    def to_pandas(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retourne les nœuds et arcs de ce graphe sous forme de DataFrame Pandas

        Returns:
            Deux DataFrames Pandas (nœuds, arcs)
        """
        nodes_df = (
            pd.DataFrame([{"sctid": n, **self.g.nodes[n]} for n in self.g.nodes])
            .set_index("sctid")
        )
        edges_df = nx.to_pandas_edgelist(self.g)
        return nodes_df, edges_df

    @property
    def relationship_types(self) -> Set[str]:
        """
        Retourne l'ensemble des attributs existants.

        Returns:
            Un Set de string
        """
        return set(nx.get_edge_attributes(self.g, "type").values())

    @staticmethod
    def from_serialized(path: str) -> Self:
        """
        Charge un graphe depuis une linéarisation.

        Args:
            path: Chemin + nom du fichier sauvegardé.

        Returns:
            Un objet Graphe.
        """
        g = nx.read_gml(path, destringizer=int)
        return Graphe(g)

    @staticmethod
    def get_core_file_paths(path: str, lang: str = "fr") -> Tuple[str]:
        """
        Génère les chemins vers les fichiers d'intérêts au sein d'une archive RF2.

        Args:
            path: Chemin vers l'archive RF2.
            lang: Autre langue que l'anglais présente dans la release, par défaut 'fr'.

        Returns:
            Un Tuple contenant les fichiers de concepts, descriptions et relations.
        """
        # Normaliser le chemin de l'archive RF2
        path = op.abspath(path)
        # Vérification de l'existance du dossier
        if not op.exists(path):
            raise AssertionError(f"Le chemin '{path}' n'existe pas")

        try:
            # Récupération des différents éléments à partir du nom du dossier
            elements = path.split("_")
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

        termino_path = op.join(path, "Snapshot/Terminology")

        # Création et vérification de l'existence du fichier des concepts
        concepts_path = op.join(termino_path,
                                f"sct2_Concept_Snapshot_{ns}_{date}.txt")
        if not op.exists(concepts_path):
            raise AssertionError(f"Le chemin '{concepts_path}' n'existe pas")

        if lang:
            # Création et vérification de l'existence du fichier des descriptions anglaises
            en_desc_path = op.join(termino_path,
                                   f"sct2_Description_Snapshot-en_{ns}_{date}.txt")
            if not op.exists(en_desc_path):
                raise AssertionError(f"Le chemin '{en_desc_path}' n'existe pas")

            # Création et vérification de l'existence du fichier des descriptions non anglaises
            lang_desc_path = op.join(termino_path,
                                     f"sct2_Description_Snapshot-{lang}_{ns}_{date}.txt")
            if not op.exists(lang_desc_path):
                raise AssertionError(f"Le chemin '{lang_desc_path}' n'existe pas")
        else:
            # Création et vérification de l'existence du fichier des descriptions anglaises
            en_desc_path = op.join(termino_path,
                                   f"sct2_Description_Snapshot_{ns}_{date}.txt")
            if not op.exists(en_desc_path):
                raise AssertionError(f"Le chemin '{en_desc_path}' n'existe pas")
            # Pas de description non anglaise
            lang_desc_path = ""

        # Création et vérification de l'existence du fichier des relations
        relationships_path = op.join(termino_path,
                                     f"sct2_Relationship_Snapshot_{ns}_{date}.txt")
        if not op.exists(relationships_path):
            raise AssertionError(f"Le chemin '{relationships_path}' n'existe pas")

        return concepts_path, en_desc_path, lang_desc_path, relationships_path

    @staticmethod
    def from_rf2(path: str, lang: str = "fr") -> Self:
        """
        Crée un Graphe depuis une archive RF2.

        Args:
            path: Chemin vers l'archive RF2.
            lang: Autre langue que l'anglais présente dans la release, par défaut 'fr'.

        Returns:
            Un objet Graphe.
        """
        c_path, en_desc_path, lang_desc_path, rs_path = Graphe.get_core_file_paths(path)

        # Charge les concepts
        print("Lecture du fichier des concepts ...")
        concept = pd.read_csv(c_path, sep="\t", dtype=str, usecols=["id", "active"])
        concept = concept.loc[concept.loc[:, "active"] == "1"]

        # Charge les descriptions
        print("Lecture du ou des fichier(s) des descriptions...")
        desc = pd.read_csv(en_desc_path, dtype=str, quoting=3, encoding="UTF-8",
                           sep="\t", usecols=["active", "conceptId", "languageCode",
                                              "typeId", "term"])
        if lang:
            desc = pd.concat([
                desc,
                pd.read_csv(lang_desc_path, sep="\t", dtype=str, quoting=3, encoding="UTF-8",
                            usecols=["active", "conceptId", "languageCode", "typeId", "term"])
            ])

        desc = desc.loc[desc.loc[:, "active"] == "1"]
        # Supprime les descriptions actives de concepts inactifs
        desc = desc.loc[desc.loc[:, "conceptId"].isin(concept.loc[:, "id"])]
        # Division par langue
        syn_en = desc.loc[(desc.loc[:, "typeId"] != "900000000000003001")
                          & (desc.loc[:, "languageCode"] == "en")]
        syn_lang = desc.loc[(desc.loc[:, "typeId"] != "900000000000003001")
                            & (desc.loc[:, "languageCode"] == lang)]

        # Charge les relations
        print("Lecture du fichier des relations...")
        relations = pd.read_csv(rs_path, sep="\t", dtype=str,
                                usecols=["active", "sourceId", "destinationId",
                                         "relationshipGroup", "typeId"])
        relations = relations.loc[relations.loc[:, "active"] == "1"]

        # Crée l'index des attributs
        attributs = desc.loc[desc.loc[:, "conceptId"].isin(relations.loc[:, "typeId"].unique())]
        attributs = attributs.loc[attributs.loc[:, "typeId"] == "900000000000003001"]
        attributs.set_index("conceptId", inplace=True)
        attributs = attributs.loc[:, "term"].to_dict()

        # Création du DataFrame des nœuds
        nodes = desc.loc[(desc.loc[:, "typeId"] == "900000000000003001")
                         & (desc.loc[:, "languageCode"] == "en"), ["conceptId", "term"]]
        nodes.set_index("conceptId", inplace=True)
        nodes = pd.concat([nodes, syn_en.groupby("conceptId")["term"].apply(list)], axis=1)
        nodes = pd.concat([nodes, syn_lang.groupby("conceptId")["term"].apply(list)], axis=1)
        nodes.reset_index(inplace=True, col_level=0)
        nodes.columns = ["node_id", "fsn", "syn_en", "syn_fr"]

        # Initialisation du graphe
        print(f"Lecture de {len(nodes)} concepts et {len(relations)} relations du RF2.")
        g = nx.DiGraph()

        # Création des nœuds
        print("\nCréation des concepts...")
        g.add_nodes_from((id, dict(row)) for id, row in tqdm(nodes.iterrows(), total=len(nodes)))

        # Crée les relations
        print("Création des relations...")
        for r in tqdm(relations.to_dict(orient="records")):
            g.add_edge(
                r["sourceId"],
                r["destinationId"],
                group=r["relationshipGroup"],
                type=attributs[r["typeId"]],
                type_id=r["typeId"]
            )

        # Retourne le graphe complet
        return Graphe(g)
