import pandas as pd

from pathlib import Path
from snomed_graphe import io


def test_rf2_paths(tmp_path: Path, concept_file: pd.DataFrame, desc_en_file: pd.DataFrame,
                   desc_fr_file: pd.DataFrame, en_accept_file: pd.DataFrame,
                   fr_accept_file: pd.DataFrame, relationship_file: pd.DataFrame) -> None:
    dir = tmp_path / "SnomedCT_ManagedServiceFR_PRODUCTION_FR1000315_20240621T120000Z"
    dir.mkdir()
    snap = dir / "Snapshot"
    snap.mkdir()
    terminology = snap / "Terminology"
    terminology.mkdir()
    refset = snap / "Refset"
    refset.mkdir()
    lang_refset = refset / "Language"
    lang_refset.mkdir()

    c_file = terminology / "sct2_Concept_Snapshot_FR1000315_20240621.txt"
    en_d_file = terminology / "sct2_Description_Snapshot-en_FR1000315_20240621.txt"
    fr_d_file = terminology / "sct2_Description_Snapshot-fr_FR1000315_20240621.txt"
    r_file = terminology / "sct2_Relationship_Snapshot_FR1000315_20240621.txt"
    en_a_file = lang_refset / "der2_cRefset_LanguageSnapshot-en_FR1000315_20240621.txt"
    fr_a_file = lang_refset / "der2_cRefset_LanguageSnapshot-fr_FR1000315_20240621.txt"

    concept_file.to_csv(c_file, sep="\t", encoding="UTF-8", index=False)
    desc_en_file.to_csv(en_d_file, sep="\t", encoding="UTF-8", index=False)
    desc_fr_file.to_csv(fr_d_file, sep="\t", encoding="UTF-8", index=False)
    relationship_file.to_csv(r_file, sep="\t", encoding="UTF-8", index=False)
    en_accept_file.to_csv(en_a_file, sep="\t", encoding="UTF-8", index=False)
    fr_accept_file.to_csv(fr_a_file, sep="\t", encoding="UTF-8", index=False)

    path = io._rf2_paths(dir, "fr")

    assert path == (str(c_file), str(en_d_file), str(en_a_file), str(fr_d_file), str(fr_a_file),
                    str(r_file))


def test_get_descriptions(tmp_path: Path, concept_file: pd.DataFrame, desc_en_file: pd.DataFrame,
                          desc_fr_file: pd.DataFrame, desc: pd.DataFrame) -> None:
    dir = tmp_path / "sub"
    dir.mkdir()

    c_file = dir / "concept.txt"
    en_file = dir / "en_desc.txt"
    fr_file = dir / "fr_desc.txt"

    concept_file.to_csv(c_file, sep="\t", encoding="UTF-8", index=False)
    desc_en_file.to_csv(en_file, sep="\t", encoding="UTF-8", index=False)
    desc_fr_file.to_csv(fr_file, sep="\t", encoding="UTF-8", index=False)

    pd.testing.assert_frame_equal(io._get_descriptions(c_file, en_file, fr_file), desc)


def test_set_acceptability(tmp_path: Path, desc: pd.DataFrame, en_accept_file: pd.DataFrame,
                           fr_accept_file: pd.DataFrame, desc_accept: pd.DataFrame) -> None:
    dir = tmp_path / "sub"
    dir.mkdir()

    en_file = dir / "en_accept.txt"
    fr_file = dir / "fr_accept.txt"

    en_accept_file.to_csv(en_file, sep="\t", encoding="UTF-8", index=False)
    fr_accept_file.to_csv(fr_file, sep="\t", encoding="UTF-8", index=False)

    pd.testing.assert_frame_equal(io._set_acceptability(desc, en_file, fr_file, "fr"), desc_accept)


def test_get_relations(tmp_path: Path, relationship_file: pd.DataFrame, rel: pd.DataFrame) -> None:
    dir = tmp_path / "sub"
    dir.mkdir()

    rs_file = dir / "relationship.txt"
    relationship_file.to_csv(rs_file, sep="\t", encoding="UTF-8", index=False)

    pd.testing.assert_frame_equal(io._get_relations(rs_file), rel)


def test_get_nodes_details(desc_accept: pd.DataFrame, nodes: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(io._get_nodes_details(desc_accept, "fr"), nodes)


def test_from_rf2(tmp_path: Path, concept_file: pd.DataFrame, desc_en_file: pd.DataFrame,
                  desc_fr_file: pd.DataFrame, en_accept_file: pd.DataFrame,
                  fr_accept_file: pd.DataFrame, relationship_file: pd.DataFrame) -> None:
    dir = tmp_path / "SnomedCT_ManagedServiceFR_PRODUCTION_FR1000315_20240621T120000Z"
    dir.mkdir()
    snap = dir / "Snapshot"
    snap.mkdir()
    terminology = snap / "Terminology"
    terminology.mkdir()
    refset = snap / "Refset"
    refset.mkdir()
    lang_refset = refset / "Language"
    lang_refset.mkdir()

    c_file = terminology / "sct2_Concept_Snapshot_FR1000315_20240621.txt"
    en_d_file = terminology / "sct2_Description_Snapshot-en_FR1000315_20240621.txt"
    fr_d_file = terminology / "sct2_Description_Snapshot-fr_FR1000315_20240621.txt"
    r_file = terminology / "sct2_Relationship_Snapshot_FR1000315_20240621.txt"
    en_a_file = lang_refset / "der2_cRefset_LanguageSnapshot-en_FR1000315_20240621.txt"
    fr_a_file = lang_refset / "der2_cRefset_LanguageSnapshot-fr_FR1000315_20240621.txt"

    concept_file.to_csv(c_file, sep="\t", encoding="UTF-8", index=False)
    desc_en_file.to_csv(en_d_file, sep="\t", encoding="UTF-8", index=False)
    desc_fr_file.to_csv(fr_d_file, sep="\t", encoding="UTF-8", index=False)
    relationship_file.to_csv(r_file, sep="\t", encoding="UTF-8", index=False)
    en_accept_file.to_csv(en_a_file, sep="\t", encoding="UTF-8", index=False)
    fr_accept_file.to_csv(fr_a_file, sep="\t", encoding="UTF-8", index=False)

    sct = io.from_rf2(dir, "fr")

    assert (list(sct.g.nodes), list(sct.g.edges)) == (["1009", "2009", "4009"], [("1009", "2009")])
