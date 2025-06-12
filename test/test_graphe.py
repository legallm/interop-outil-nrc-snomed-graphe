import pandas as pd
import pytest

from snomed_graphe.graphe import SnomedGraph
from typing import Dict, List, Tuple, Union

###############################
# Tests des méthodes internes #
###############################


def test_in_relationships(sct: SnomedGraph, in_rel: List[Tuple[str]]) -> None:
    answer = [(r.src.sctid, r.attribute.sctid, r.tgt.sctid)
              for r in sct._in_relationships("129574000")]

    assert answer == in_rel


def test_out_relationships(sct: SnomedGraph, out_rel: List[Tuple[str]]) -> None:
    answer = [(r.src.sctid, r.attribute.sctid, r.tgt.sctid)
              for r in sct._out_relationships("129574000")]

    assert answer == out_rel


#####################################################
# Tests des méthodes d'accès aux éléments du graphe #
#####################################################


def test_get_concept_details(sct: SnomedGraph, details: Dict[str, str]) -> None:
    c = sct.get_concept_details("129574000")
    attributs = {a: getattr(c, a) for a in dir(c) if not a.startswith("__")}

    assert attributs == details


def test_get_full_concept(sct: SnomedGraph, full: Dict[str, Union[str, Dict]]) -> None:
    c = sct.get_full_concept("129574000")
    attributs = {a: getattr(c, a) for a in dir(c) if not a.startswith("__")}

    attributs["children"] = [c.sctid for c in attributs["children"]]
    del attributs["concept_details"]
    attributs["parents"] = [c.sctid for c in attributs["parents"]]
    attributs["relationships"] = {k: [(r.attribute.sctid, r.tgt.sctid) for r in v]
                                  for k, v in attributs["relationships"].items()}

    assert attributs == full


def test_get_grouped_relationships(sct: SnomedGraph,
                                   grouped_rel: Dict[str, List[Tuple[str]]]) -> None:
    rel = {k: [(r.attribute.sctid, r.tgt.sctid) for r in v]
           for k, v in sct.get_grouped_relationships("129574000").items()}

    assert rel == grouped_rel


def test_get_ungrouped_relationships(sct: SnomedGraph, ungrouped_rel: List[Tuple[str]]) -> None:
    rel = [(r.attribute.sctid, r.tgt.sctid)
           for r in sct.get_ungrouped_relationships("129574000")]

    assert rel == ungrouped_rel


########################################################
# Tests des méthodes d'accès à la hiérarchie du graphe #
########################################################


def test_get_ancestors(sct: SnomedGraph, ancestors: List[str]) -> None:
    a = [a.sctid for a in sct.get_ancestors("129574000")]
    a.sort()

    assert a == ancestors


def test_get_children(sct: SnomedGraph, children: List[str]) -> None:
    c = [c.sctid for c in sct.get_children("129574000")]
    c.sort()

    assert c == children


def test_get_descendants(sct: SnomedGraph, descendants: List[str]) -> None:
    d = [d.sctid for d in sct.get_descendants("129574000")]
    d.sort()

    assert d == descendants


def test_get_neighbors(sct: SnomedGraph, neighbors: List[str]) -> None:
    n = [n.sctid for n in sct.get_neighbors("129574000", 3)]
    n.sort()

    assert n == neighbors


def test_get_parents(sct: SnomedGraph, parents: List[str]) -> None:
    p = [a.sctid for a in sct.get_parents("129574000")]

    assert p == parents


############################################
# Tests des méthodes de calcul des chemins #
############################################


def test_hierarchical_path(sct: SnomedGraph, hierarchical_path: List[str]) -> None:
    p = [c.sctid for c in sct.hierarchical_path("test", "138875005")]

    assert p == hierarchical_path


def test_hierarchical_path_direction(sct: SnomedGraph) -> None:
    path_up = [c.sctid for c in sct.hierarchical_path("test", "138875005")]
    path_down = [c.sctid for c in sct.hierarchical_path("138875005", "test")]

    assert path_up == path_down[::-1]


def test_hierarchical_path_to_root(sct: SnomedGraph) -> None:
    path = [c.sctid for c in sct.hierarchical_path("test", "138875005")]
    path_root = [c.sctid for c in sct.hierarchical_path_to_root("test")]

    assert path == path_root


def test_path(sct: SnomedGraph, path: List[str]) -> None:
    p = [c.sctid for c in sct.path("1163440003", "362981000")]

    assert p == path


def test_path_direction(sct: SnomedGraph) -> None:
    path_up = [c.sctid for c in sct.path("1163440003", "362981000")]
    path_down = [c.sctid for c in sct.path("362981000", "1163440003")]

    assert path_up == path_down[::-1]


################################################################
# Test des méthodes de manipulation & transformation du graphe #
################################################################


def test_graph_to_pandas_nodes(sct: SnomedGraph, df_nodes: pd.DataFrame) -> None:
    sct_nodes, _ = sct.graph_to_pandas()

    pd.testing.assert_frame_equal(sct_nodes, df_nodes)


def test_graph_to_pandas_edges(sct: SnomedGraph, df_edges: pd.DataFrame) -> None:
    _, sct_edges = sct.graph_to_pandas()
    sct_edges = sct_edges[["source", "target", "group", "src", "attribute", "tgt"]]

    pd.testing.assert_frame_equal(sct_edges, df_edges)


def test_desc_to_pandas(sct: SnomedGraph, df_desc: pd.DataFrame) -> None:
    desc = sct.desc_to_pandas()
    desc.reset_index(drop=True, inplace=True)

    pd.testing.assert_frame_equal(desc, df_desc)


def test_subgraph(sct: SnomedGraph, sub_sct: SnomedGraph) -> None:
    sub = sct.subgraph("311793000", True, True)

    sub_n = list(sub.g.nodes)
    sub_n.sort()
    sub_e = list(sub.g.edges)
    sub_e.sort()
    sub_sct_n = list(sub_sct.g.nodes)
    sub_sct_n.sort()
    sub_sct_e = list(sub_sct.g.edges)
    sub_sct_e.sort()

    assert (sub_n, sub_e) == (sub_sct_n, sub_sct_e)


def test_search_in_desc_error(sct: SnomedGraph) -> None:
    with pytest.raises(ValueError):
        sct.search_in_desc("myocarde", accept="valeur incorrecte")


def test_search_in_desc_default(sct: SnomedGraph, search: List[str]) -> None:
    s = sct.search_in_desc("myo")
    s.sort()

    assert s == search


def test_search_in_desc_syn(sct: SnomedGraph, search_syn: List[str]) -> None:
    s = sct.search_in_desc("myo", accept="ACCEPT")
    s.sort()

    assert s == search_syn


def test_search_in_desc_pt(sct: SnomedGraph, search_pt: List[str]) -> None:
    s = sct.search_in_desc("myo", accept="PREF")
    s.sort()

    assert s == search_pt


def test_search_in_desc_fsn(sct: SnomedGraph, search_fsn: List[str]) -> None:
    s = sct.search_in_desc("myo", fsn="disorder")
    s.sort()

    assert s == search_fsn


def test_search_in_desc_absent(sct: SnomedGraph, search_absent: List[str]) -> None:
    s = sct.search_in_desc("myo", is_in=False)
    s.sort()

    assert s == search_absent
