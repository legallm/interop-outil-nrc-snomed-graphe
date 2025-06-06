from typing import Any, Dict, List, Union


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
    def __init__(self, src: ConceptDetails, tgt: Union[int, ConceptDetails], group: str,
                 attribute: ConceptDetails) -> None:
        self.src = src
        self.tgt = tgt
        self.group = group
        self.attribute = attribute

    def __repr__(self) -> str:
        return f"--{self.attribute}--> {self.tgt}"


class Concept():
    """
    Une classe pour représenter un concept SNOMED CT.
    """
    def __init__(self, concept_details: ConceptDetails, parents: List[ConceptDetails],
                 children: List[ConceptDetails],
                 relationships: Dict[int, List[Relationship]], lang: str = "fr") -> None:
        self.concept_details = concept_details
        self.relationships = relationships
        self.parents = parents
        self.children = children
        self.lang = lang

    def __repr__(self) -> str:
        str_ = str(self.concept_details)
        str_ += f"\n\nPT en :\n{self.concept_details.pt_en}"
        str_ += f"\n\nPT {self.lang} :\n{self.concept_details.pt_lang}"
        str_ += f"\n\nSYN en:\n{self.concept_details.syn_en}"
        str_ += f"\n\nSYN {self.lang} :\n{self.concept_details.syn_lang}"
        str_ += "\n\nParents :\n"
        str_ += "\n".join([str(p) for p in self.parents])
        str_ += "\n\nEnfants :\n"
        str_ += "\n".join([str(c) for c in self.children])
        str_ += "\n\nRelations :\n"
        str_ += "\n".join(f"{k}:\n   {v}\n" for k, v in self.relationships.items())
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
