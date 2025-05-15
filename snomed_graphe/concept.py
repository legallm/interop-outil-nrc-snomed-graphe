import re
from typing import Any, List


class ConceptDetails():
    """
    Une classe pour représenter les détails essentiels d'un concept SNOMED CT
    """
    def __init__(self, sctid: int, fsn: str, synonyms: List[str] = None) -> None:
        self.sctid = sctid
        self.fsn = fsn
        self.synonyms = synonyms

    def __repr__(self) -> str:
        return f"{self.sctid} | {self.fsn}"

    def __eq__(self, other) -> Any:
        return self.sctid == other.sctid

    def __hash__(self) -> int:
        return int(self.sctid)

    @property
    def hierarchy(self) -> str:
        hierarchy_match = re.search(r'\(([^)]+)\)\s*$', self.fsn)
        if hierarchy_match:
            return hierarchy_match[0][1:-1]
        else:
            return ""


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
    def __init__(self, concept_details, parents, children, inferred_relationship_groups) -> None:
        self.concept_details = concept_details
        self.inferred_relationship_groups = inferred_relationship_groups
        self.parents = parents
        self.children = children

    def __repr__(self) -> str:
        str_ = str(self.concept_details)
        str_ += f"\n\nSynonyms:\n{self.concept_details.synonyms}"
        str_ += "\n\nParents:\n"
        str_ += "\n".join([str(p) for p in self.parents])
        str_ += "\n\nChildren:\n"
        str_ += "\n".join([str(c) for c in self.children])
        str_ += "\n\nInferred Relationships:\n"
        str_ += "\n".join([str(rg) for rg in self.inferred_relationship_groups])
        return str_

    @property
    def sctid(self) -> int:
        return self.concept_details.sctid

    @property
    def fsn(self) -> str:
        return self.concept_details.fsn

    @property
    def synonyms(self) -> List[str]:
        return self.concept_details.synonyms

    @property
    def hierarchy(self) -> str:
        return self.concept_details.hierarchy
