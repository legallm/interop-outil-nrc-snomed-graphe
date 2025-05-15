import pandas as pd
import networkx as nx
from tqdm import tqdm
from itertools import groupby
from itertools import pairwise
from typing import Any, Dict, Generator, List, Self, Set, Tuple
import os
from datetime import datetime
from snomed_graphe import concept as sct


class Graphe():
    """
    Une classe pour représenter une release SNOMED CT sous forme de graphe via NetworkX.

    Attributes
    ----------
    g : nx.DiGraph
        Graphe de données
    """
    fsn_typeId = 900000000000003001
    is_a_relationship_typeId = 116680003
    root_concept_id = 138875005
    default_langcode = "en"

    def __init__(self, g: nx.DiGraph) -> None:
        """
        Crée une nouvelle instance de Graphe via un objet NetworkX DiGraph

        Args:
            g: Un DiGraph créé par Graphe.from_rf2() ou Graphe.from_serialized().
        """
        self.g = g
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
            if r.type_id == Graphe.is_a_relationship_typeId
        ]

    def get_parents(self, sctid: int) -> List[sct.ConceptDetails]:
        return [
            r.tgt for r in self.__get_out_relationships(sctid)
            if r.type_id == Graphe.is_a_relationship_typeId
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
            if r.type_id != Graphe.is_a_relationship_typeId
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
        return set([a for a in ancestors if not a.sctid == Graphe.root_concept_id])

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
            if n.sctid not in [sctid, Graphe.root_concept_id]
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
        for nodes in nx.all_simple_paths(self.g, sctid, self.root_concept_id):
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
    def get_core_file_paths(path: str, langcode: str = "en") -> Tuple[str]:
        if not os.path.exists(path):
            raise AssertionError(f'The path "{path}" does not exist')
        base_dir = os.path.dirname(path)
        dir = os.path.basename(path)
        try:
            elements = dir.split("_")
            assert len(elements) in [4, 5]
            if len(elements) == 5:
                filetype, contenttype, contentsubtype, countrynamespace, versiondate = elements
            else:
                filetype, contenttype, contentsubtype, versiondate = elements
                countrynamespace = "INT"
            versiondate = datetime.strptime(versiondate, "%Y%m%dT%H%M%SZ").strftime("%Y%m%d")
        except (AttributeError, ValueError, AssertionError):
            raise AssertionError(
                f'Le dossier "{dir}" ne semble pas suivre la convention de nommage RF2.'
            )
        else:
            relationships_path = f"{base_dir}/{dir}/Snapshot/Terminology/sct2_Relationship_Snapshot_{countrynamespace}_{versiondate}.txt"
            if not os.path.exists(relationships_path):
                raise AssertionError(f'The path "{relationships_path}" does not exist')
            descriptions_path = f"{base_dir}/{dir}/Snapshot/Terminology/sct2_Description_Snapshot-{langcode}_{countrynamespace}_{versiondate}.txt"
            if not os.path.exists(descriptions_path):
                raise AssertionError(f'The path "{descriptions_path}" does not exist')
        return relationships_path, descriptions_path

    @staticmethod
    def from_rf2(path: str) -> Self:
        """
        Crée un Graphe depuis une archive RF2.

        Args:
            path: Chemin vers l'archive RF2.

        Returns:
            Un objet Graphe.
        """
        relationships_path, descriptions_path = Graphe.get_core_file_paths(path)

        # Charge les relations
        relationships_df = pd.read_csv(relationships_path, delimiter="\t")
        relationships_df = relationships_df[relationships_df.active == 1]

        # Charge les concepts
        concepts_df = pd.read_csv(descriptions_path, delimiter="\t")
        concepts_df = concepts_df[concepts_df.active == 1]
        concepts_df.set_index("conceptId", inplace=True)

        # Crée l'index des attributs
        relationship_types = concepts_df.loc[relationships_df.typeId.unique()]
        relationship_types = relationship_types[relationship_types.typeId == Graphe.fsn_typeId]
        relationship_types = relationship_types.term.to_dict()

        # Initialise le graphe
        n_concepts = concepts_df.shape[0]
        n_relationships = relationships_df.shape[0]
        print(f"{n_concepts} concepts et {n_relationships} relations extraite du RF2.")
        g = nx.DiGraph()

        # Crée les relations
        print("Création des Relations...")
        for r in tqdm(relationships_df.to_dict(orient="records")):
            g.add_edge(
                r["sourceId"],
                r["destinationId"],
                group=r["relationshipGroup"],
                type=relationship_types[r["typeId"]],
                type_id=r["typeId"]
            )

        # Ajout des concepts
        print("Ajout des Concepts...")
        for sctid, rows in tqdm(concepts_df.groupby(concepts_df.index)):
            synonyms = [row.term for _, row in rows.iterrows() if row.typeId != Graphe.fsn_typeId]
            try:
                fsn = rows[rows.typeId == Graphe.fsn_typeId].term.values[0]
            except IndexError:
                fsn = synonyms[0]
                synonyms = synonyms[1:]
                print(f"Concept with SCTID {sctid} has no FSN. Using synonym '{fsn}' instead.")
            g.add_node(sctid, fsn=fsn, synonyms=synonyms)

        # Suppression des nœuds isolés
        g.remove_nodes_from(list(nx.isolates(g)))

        # Initialise la classe
        return Graphe(g)
