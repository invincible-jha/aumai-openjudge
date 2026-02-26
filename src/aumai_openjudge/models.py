"""Pydantic v2 models for aumai-openjudge legal case analysis with IPC/BNS mapping."""

from __future__ import annotations

from pydantic import BaseModel, Field

LEGAL_DISCLAIMER = (
    "This tool does not provide legal advice."
    " Consult a qualified legal professional."
)

__all__ = ["LegalSection", "CaseAnalysis", "LegalMapping", "LEGAL_DISCLAIMER"]


class LegalSection(BaseModel):
    """A section of Indian law (IPC, BNS, CrPC, or BNSS)."""

    code: str = Field(
        ...,
        description="Legal code: IPC, BNS, CrPC, or BNSS",
        pattern="^(IPC|BNS|CrPC|BNSS|IT Act|POCSO)$",
    )
    section_number: str = Field(..., description="Section number (e.g. '302', '100')")
    title: str = Field(..., description="Short title of the section")
    description: str = Field(..., description="Full description of the provision")
    punishment: str | None = Field(
        default=None, description="Prescribed punishment, if applicable"
    )
    bailable: bool | None = Field(
        default=None, description="Whether the offence is bailable (True) or non-bailable (False)"
    )


class CaseAnalysis(BaseModel):
    """Analysis of a legal case description against relevant law sections."""

    case_description: str = Field(..., description="The original case description text")
    relevant_sections: list[LegalSection] = Field(
        ..., description="Law sections relevant to the case"
    )
    ipc_to_bns_mapping: list[dict[str, object]] = Field(
        default_factory=list,
        description="IPC to BNS mapping for sections found in the case",
    )
    summary: str = Field(..., description="Human-readable summary of the legal analysis")
    disclaimer: str = Field(
        default=LEGAL_DISCLAIMER,
        description="Mandatory legal disclaimer",
    )


class LegalMapping(BaseModel):
    """Mapping between an old IPC/CrPC section and its new BNS/BNSS equivalent."""

    old_code: str = Field(..., description="Old code name (IPC or CrPC)")
    old_section: str = Field(..., description="Old section number")
    new_code: str = Field(..., description="New code name (BNS or BNSS)")
    new_section: str = Field(..., description="New section number")
    status: str = Field(
        ...,
        description="Status of the mapping: replaced, amended, or repealed",
        pattern="^(replaced|amended|repealed)$",
    )
