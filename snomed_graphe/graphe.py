import networkx as nx
import pandas as pd
import snomed_graphe.component as sct

from collections import defaultdict
from typing import Any, Dict, Generator, List, Self, Tuple


class SnomedGraph():
    """
    Une classe pour représenter une release SNOMED CT sous forme de graphe via NetworkX.
    """
    def __init__(self, g: nx.DiGraph, lang: str = "fr", root: str = "138875005") -> None:
        """
        Crée une nouvelle instance de Graphe via un objet NetworkX DiGraph

        Args:
            g: Un DiGraph créé par Graphe.from_rf2() ou Graphe.from_serialized().
            lang: Langue autre que l'anglais utilisée dans le graphe.
            root: SCTID du concept racine du Graphe.
        """
        self.g = g
        self.undir = nx.to_undirected(self.g)
        self.lang = lang
        self.root = root
        print(self)

    def __contains__(self, item) -> bool:
        return item in self.g

    def __iter__(self) -> Generator[Any, Any, None]:
        for sctid in self.g.nodes:
            yield self.g.nodes[sctid]

    def __len__(self) -> int:
        return self.g.number_of_nodes()

    def __repr__(self) -> str:
        return f"{self.g.number_of_nodes()} concepts et {self.g.number_of_edges()} relations."

    #####################
    # Méthodes internes #
    #####################
    def _in_relationships(self, sctid: str) -> Generator[Dict, None, None]:
        """Retourne les relations pointant vers le concept `sctid`.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns
            Générateur des relations pointant vers le concept.
        """
        t = self.get_concept_details(sctid)
        return (
            sct.Relationship(
                self.get_concept_details(s),
                t,
                self.g.edges[(s, sctid)]["group"],
                self.get_concept_details(a)
            )
            for s, _, a in self.g.in_edges(sctid, data="attribute")
        )

    def _out_relationships(self, sctid: str) -> Generator[Dict, None, None]:
        """Retourne les relations partant du concept `sctid`.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns
            Générateur des relations partant du concept.
        """
        s = self.get_concept_details(sctid)
        return (
            sct.Relationship(
                s,
                self.get_concept_details(t),
                self.g.edges[(sctid, t)]["group"],
                self.get_concept_details(a)
            )
            for _, t, a in self.g.out_edges(sctid, data="attribute")
        )

    #############
    # Propriété #_out
    #############
    @property
    def attributes(self) -> List[sct.ConceptDetails]:
        """
        Retourne tous les attributs utilisés dans le graphe.

        Returns:
            Une liste contenant les attributs uniques utilisés dans le graphe.
        """
        return [self.get_concept_details(a)
                for a in set(nx.get_edge_attributes(self.g, "type").values())]

    ###########################################
    # Méthodes d'accès aux éléments du graphe #
    ###########################################
    def get_concept_details(self, sctid: int) -> sct.ConceptDetails:
        """
        Renvoie les détails essentiels d'un concept : SCTID, FSN, PT et synonymes
        acceptables (SYN).

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns:
            Un objet ConceptDetails.
        """
        return sct.ConceptDetails(sctid=sctid, **self.g.nodes[sctid])

    def get_full_concept(self, sctid: int) -> sct.Concept:
        """
        Renvoie tous les détails d'un concept : SCTID, FSN, PT, synonymes,
        parents, enfants et relations non hiérarchiques.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns:
            Un objet Concept.
        """
        return sct.Concept(
            self.get_concept_details(sctid),
            self.get_parents(sctid),
            self.get_children(sctid),
            self.get_grouped_relationships(sctid),
            self.lang
        )

    def get_grouped_relationships(self, sctid: int) -> Dict[str, List[sct.Relationship]]:
        """
        Renvoie la liste des relations non hiérarchiques d'un concept avec les groupes
        relationnels.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns:
            Un dictionnaire des relations non hiérarchiques regroupées par groupe relationnel.
        """
        relationship = defaultdict(list)
        {relationship[rel.group].append(rel) for rel in self._out_relationships(sctid)
         if rel.attribute.sctid != "116680003"}
        return dict(relationship)

    def get_ungrouped_relationships(self, sctid: int) -> List[sct.Relationship]:
        """
        Renvoie la liste brute des relations non hiérarchiques d'un concept.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns:
            Une liste des relations non hiérarchiques.
        """
        return [rel for rel in self._out_relationships(sctid)
                if rel.attribute.sctid != "116680003"]

    ##############################################
    # Méthodes d'accès à la hiérarchie du graphe #
    ##############################################
    def get_ancestors(self, sctid: str, degree: int = 999999) -> List[sct.ConceptDetails]:
        """
        Renvoie les ancêtres d'un concept.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.
            degree: Le nombre de niveau à remonter dans la hiérarchie
                (999999 par défaut, soit tous les ancêtres).

        Returns:
            Liste des ancêtres.
        """
        ancestors = nx.single_source_dijkstra_path_length(
            self.g, sctid, degree, lambda s, t, a: 1 if a["attribute"] == "116680003" else None
        )
        return [self.get_concept_details(t) for t in ancestors.keys() if ancestors[t] > 0]

    def get_children(self, sctid: int) -> List[sct.ConceptDetails]:
        """
        Renvoie les enfants d'un concept.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns
            La liste des SCTIDs des enfants.
        """
        return [rel.src for rel in self._in_relationships(sctid)
                if rel.attribute.sctid == "116680003"]

    def get_descendants(self, sctid: str, degree: int = 999999) -> List[sct.ConceptDetails]:
        """
        Renvoie les descendants d'un concept.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.
            degree: Le nombre de niveau à descendre dans la hiérarchie
                (999999 par défaut, soit tous les descendants).

        Returns:
            Liste des descendants.
        """
        filter = nx.ancestors(self.g, sctid)
        descendants = set(nx.single_source_dijkstra_path_length(
            self.undir, sctid, degree, lambda s, t, a: 1 if a["attribute"] == "116680003" else None
        ).keys())
        descendants = descendants.intersection(filter)

        return [self.get_concept_details(id) for id in descendants]

    def get_neighbors(self, sctid: int, degree: int = 1) -> List[sct.ConceptDetails]:
        """
        Renvoie les voisins d'un concept. Les voisins comprennent les ancêtres, descendants et
        cousins jusqu'à un certain degré `degree`.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.
            degree: Le nombre de niveau à remonter ou descendre dans la hiérarchie
                (1 par défaut, soit les parents et les enfants).

        Returns:
            Une liste des voisins.
        """
        target = nx.single_source_dijkstra_path_length(
            self.undir, sctid, degree, lambda s, t, a: 1 if a["attribute"] == "116680003" else None
        )
        return [self.get_concept_details(t) for t in target.keys()]

    def get_parents(self, sctid: str) -> List[sct.ConceptDetails]:
        """
        Renvoie les parents d'un concept.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT.

        Returns
            La liste des SCTIDs des parents.
        """
        return [rel.tgt for rel in self._out_relationships(sctid)
                if rel.attribute.sctid == "116680003"]

    ################################
    # Méthodes d'analyse du graphe #
    ################################
    def hierarchical_path(self, src: int, tgt: int) -> List[sct.ConceptDetails]:
        """
        Retourne le chemin le plus court entre les concepts en utilisant uniquement les relations
        hiérarchiques via l'algorithme de Dijkstra.

        Args:
            src: Identifiant valide d'un concept SNOMED CT source.
            tgt: Identifiant valide d'un concept SNOMED CT cible.

        Returns:
            Une liste des concepts formant le chemin entre la source et la cible.
        """
        return [self.get_concept_details(c) for c in nx.dijkstra_path(
            self.undir, src, tgt, lambda s, t, a: 1 if a["attribute"] == "116680003" else None)
        ]

    def hierarchical_path_to_root(self, sctid: int) -> List[sct.ConceptDetails]:
        """
        Retourne le chemin le plus court entre le concept et la racine du graphe en utilisant
        uniquement les relations hiérarchiques via l'algorithme de Dijkstra.

        Args:
            sctid: Identifiant valide d'un concept SNOMED CT

        Returns:
            Une liste des concepts formant le chemin entre le concept et la racine.
        """
        return self.path(sctid, self.root)

    def path(self, src: int, tgt: int) -> List[sct.ConceptDetails]:
        """
        Retourne le chemin le plus court entre les concepts en utilisant les relations
        hiérarchiques et non hiérarchiques via l'algorithme de Dijkstra.

        Args:
            src: Identifiant valide d'un concept SNOMED CT source.
            tgt: Identifiant valide d'un concept SNOMED CT cible.

        Returns:
            Une liste des concepts formant le chemin entre la source et la cible.
        """
        return [self.get_concept_details(c) for c in nx.dijkstra_path(self.undir, src, tgt)]

    #######################################################
    # Méthodes de manipulation & transformation du graphe #
    #######################################################
    def to_pandas(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Transforme le graphe en deux DataFrame Pandas (nœuds et arcs).

        Returns:
            Tuple contenant le DataFrame des nœuds et celui des arcs.
        """
        nodes_df = (
            pd.DataFrame([{"sctid": n, **self.g.nodes[n]} for n in self.g.nodes])
            .set_index("sctid")
        )
        edges_df = nx.to_pandas_edgelist(self.g)
        return nodes_df, edges_df

    def subgraph(self, target: str, down: str = True, up: str = False) -> Self:
        """
        Renvoie un sous-graphe centré sur un concept. Le sous-graphe peut regrouper les ancêtres
        et/ou les descendants du concept, les attributs utilisés par ces concepts, les valeurs
        de ces attributs et les ancêtres des valeurs.

        Args:
            target: Concept centre du sous-graphe.
            down: Indique si les descendants du concept sont récupérés (oui par défaut).
            up: Indique si les ancêtres du concept sont récupérés (non par défaut).

        Returns:
            Renvoie un objet SnomedGraph contenant le sous-graphe
        """
        nodes = {target}
        if down:
            # Récupère les descendants
            nodes = nodes.union({c.sctid for c in self.get_descendants(target)})
        if up:
            # Récupère les ancêtres
            nodes = nodes.union({c.sctid for c in self.get_ancestors(target)})

        # Récupère les relations non hiérarchiques de tous les concepts
        rel = [r for n in nodes for r in self.get_ungrouped_relationships(n)]

        if rel:
            # Extraire les attributs des relations non hiérarchiques
            attributes = {r.attribute.sctid for r in rel}
            # Extraire les valeurs des relations non hiérarchiques
            values = {r.tgt.sctid for r in rel}

            # Récupère les ancêtres des attributs utilisés & les attributs
            nodes = nodes.union({c.sctid for a in attributes for c in self.get_ancestors(a)})
            nodes = nodes.union(attributes)
            if down or up:
                nodes = nodes.union({"116680003"})

            # Récupère les ancêtres des valeurs d'attributs utilisées & les valeurs
            nodes = nodes.union({c.sctid for v in values for c in self.get_ancestors(v)})
            nodes = nodes.union(values)

        # Création du graphe, avec comme racine le concept centre du sous-graphe
        return SnomedGraph(self.g.subgraph(nodes).copy(), self.lang, root=target)
