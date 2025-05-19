from typing import Any, List


class ConceptDetails():
    """
    Une classe pour représenter les détails essentiels d'un concept SNOMED CT
    """
    def __init__(self, sctid: int, fsn: str, pt_en: str, pt_lang: str,
                 syn_en: List[str], syn_lang: List[str]) -> None:
        self.sctid = sctid
        self.fsn = fsn
        self.pt_en = pt_en
        self.pt_lang = pt_lang
        self.syn_en = syn_en
        self.syn_lang = syn_lang

    def __repr__(self) -> str:
        return f"{self.sctid} |{self.fsn}|"

    def __eq__(self, other) -> Any:
        return self.sctid == other.sctid

    def __hash__(self) -> int:
        return int(self.sctid)

    @property
    def semtag(self) -> str:
        return self.fsn.split(" (")[-1].rstrip(")")


class Relationship():
    """
    Une classe pour représenter une relation SNOMED CT
    """
    def __init__(self, src: ConceptDetails, tgt: ConceptDetails, group: int,
                 type: str, type_id: str) -> None:
        self.src = src
        self.tgt = tgt
        self.group = group
        self.type = type
        self.type_id = type_id

    def __repr__(self) -> str:
        return f"[{self.src}] ---[{self.type}]---> [{self.tgt}]"


class RelationshipGroup():
    """
    Une classe pour représenter un groupe relationnel SNOMED CT
    """
    def __init__(self, group: int, relationships: List[Relationship]) -> None:
        self.group = group
        self.relationships = relationships

    def __repr__(self) -> str:
        return f"Group {self.group}\n\t" + "\n\t".join([str(r) for r in self.relationships])


class Concept():
    """
    Une classe pour représenter un concept SNOMED CT.
    """
    def __init__(self, concept_details: ConceptDetails, parents: List[ConceptDetails],
                 children: List[ConceptDetails],
                 inferred_relationship_groups: List[RelationshipGroup]) -> None:
        self.concept_details = concept_details
        self.inferred_relationship_groups = inferred_relationship_groups
        self.parents = parents
        self.children = children

    def __repr__(self) -> str:
        str_ = str(self.concept_details)
        str_ += f"\n\nPT anglais :\n{self.concept_details.pt_en}"
        str_ += f"\n\nPT non anglais :\n{self.concept_details.pt_lang}"
        str_ += f"\n\nSYN anglais:\n{self.concept_details.syn_en}"
        str_ += f"\n\nSYN non anglais:\n{self.concept_details.syn_lang}"
        str_ += "\n\nParents :\n"
        str_ += "\n".join([str(p) for p in self.parents])
        str_ += "\n\nEnfants :\n"
        str_ += "\n".join([str(c) for c in self.children])
        str_ += "\n\nRelations :\n"
        str_ += "\n".join([str(rg) for rg in self.inferred_relationship_groups])
        return str_

    @property
    def sctid(self) -> int:
        return self.concept_details.sctid

    @property
    def fsn(self) -> str:
        return self.concept_details.fsn

    @property
    def pt_en(self) -> str:
        return self.concept_details.pt_en

    @property
    def pt_lang(self) -> str:
        return self.concept_details.pt_lang

    @property
    def syn_en(self) -> List[str]:
        return self.concept_details.syn_en

    @property
    def syn_lang(self) -> List[str]:
        return self.concept_details.syn_lang

    @property
    def semtag(self) -> str:
        return self.concept_details.semtag
