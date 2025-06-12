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

    ##################################
    # Méthodes de calcul des chemins #
    ##################################
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
    def graph_to_pandas(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
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
        return (nodes_df, edges_df)

    def desc_to_pandas(self, lang: str = "fr") -> pd.DataFrame:
        """
        Fournit une visualisation des descriptions sous forme de DataFrame Pandas.

        Args:
            lang: Langue autre que l'anglais utilisée dans le graphe.

        Returns:
            DataFrame représentant les descriptions du graphe.
        """
        nodes_df = (
            pd.DataFrame([{"sctid": n, **self.g.nodes[n]} for n in self.g.nodes])
            .set_index("sctid")
        )
        nodes_df.reset_index(inplace=True)

        # Restructuration des PT anglais
        nodes_en_pt = nodes_df.loc[:, ["sctid", "fsn", "pt_en"]]
        nodes_en_pt.columns = ["conceptId", "fsn", "term"]
        nodes_en_pt.loc[:, "acceptability"] = ["PREF"] * len(nodes_en_pt)
        nodes_en_pt.loc[:, "lang"] = ["en"] * len(nodes_en_pt)

        # Restructuration des synonymes anglais
        nodes_en_syn = nodes_df.loc[:, ["sctid", "fsn", "syn_en"]]
        nodes_en_syn = nodes_en_syn.explode("syn_en", ignore_index=True)
        nodes_en_syn.columns = ["conceptId", "fsn", "term"]
        nodes_en_syn.loc[:, "acceptability"] = ["ACCEPT"] * len(nodes_en_syn)
        nodes_en_syn.loc[:, "lang"] = ["en"] * len(nodes_en_syn)

        # Restructuration des PT anglais
        nodes_lang_pt = nodes_df.loc[:, ["sctid", "fsn", "pt_lang"]]
        nodes_lang_pt.columns = ["conceptId", "fsn", "term"]
        nodes_lang_pt.loc[:, "acceptability"] = ["PREF"] * len(nodes_lang_pt)
        nodes_lang_pt.loc[:, "lang"] = [lang] * len(nodes_lang_pt)

        # Restructuration des synonymes anglais
        nodes_lang_syn = nodes_df.loc[:, ["sctid", "fsn", "syn_lang"]]
        nodes_lang_syn = nodes_lang_syn.explode("syn_lang", ignore_index=True)
        nodes_lang_syn.columns = ["conceptId", "fsn", "term"]
        nodes_lang_syn.loc[:, "acceptability"] = ["ACCEPT"] * len(nodes_lang_syn)
        nodes_lang_syn.loc[:, "lang"] = [lang] * len(nodes_lang_syn)

        nodes = pd.concat([nodes_en_pt, nodes_en_syn, nodes_lang_pt, nodes_lang_syn],
                          ignore_index=True)
        return nodes.loc[nodes.loc[:, "term"] != ""]

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

    def search_in_desc(self, term: str, hierarchy: str = "", accept: str = "", is_in: bool = True,
                       lang: str = "fr", regex_term: bool = False, case_term: bool = False,
                       fsn: str = "", regex_fsn: bool = False,
                       case_fsn: bool = False) -> List[str]:
        """Chercher un terme dans les descriptions non-anglaises si le FSN contient un terme
        spécifique.

        Args:
            term: Terme à rechercher dans les descriptions non-anglaises.
            hierarchy: SCTID de la sous-hiérarchie à laquelle limiter la recherche.
            accept: Indique si `term` doit être cherché dans un terme préféré ("PREF"),
                un synonyme acceptable ("ACCEPT") ou peu importe ("").
            is_in: Indique si `term` doit être présent (True) ou absent (False).
            lang: Indique la langue dans laquelle `term` doit être choisie, par défaut "fr".
            regex_term: Indique si `term` est une regex ou non.
            case_term: Indique si la recherche doit être sensible à la casse de `term`.
            fsn: Terme à rechercher dans les FSN des concepts auxquels limiter la recherche.
            regex_fsn: Indique si `fsn` est une regex ou non.
            case_fsn: Indique si la recherche doit être sensible à la casse de `fsn`.

        Returns:
            Liste des SCTID des concepts répondant à la requête.
        """
        # Vérifier la valeur d'acceptabilité
        if accept not in ["", "PREF", "ACCEPT"]:
            raise ValueError("L'acceptabilité ne peut être que '', 'PREF' ou 'ACCEPT'.")

        # Récupérer la sous-partie de la SNOMED CT pertinente
        if hierarchy:
            df = self.subgraph(hierarchy).desc_to_pandas()
        else:
            df = self.desc_to_pandas()

        # Filtre sur l'acceptabilité
        if accept:
            df = df.loc[df.loc[:, "acceptability"] == accept]

        # Filtre sur le FSN
        if fsn:
            df = df.loc[df.loc[:, "fsn"].str.contains(fsn, regex=regex_fsn, case=case_fsn)]

        # Recherche du terme
        if is_in:
            df = df.loc[(df.loc[:, "lang"] == lang)
                        & (df.loc[:, "term"].str.contains(term, regex=regex_term, case=case_term))]
        else:
            df = df.loc[
                (df.loc[:, "lang"] == lang)
                & (~df.loc[:, "term"].str.contains(term, regex=regex_term, case=case_term))
            ]

        return list(df.loc[:, "conceptId"].unique())
