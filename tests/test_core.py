"""Comprehensive tests for aumai-openjudge core and models.

LEGAL DISCLAIMER: This test suite is for software testing purposes only.
The legal information in this codebase does not constitute legal advice.
Consult a qualified legal professional for any legal matters.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from aumai_openjudge.core import CaseAnalyzer, LegalCodeDatabase
from aumai_openjudge.models import (
    LEGAL_DISCLAIMER,
    CaseAnalysis,
    LegalMapping,
    LegalSection,
)

# ---------------------------------------------------------------------------
# Legal disclaimer
# ---------------------------------------------------------------------------

DISCLAIMER_TEXT = (
    "This tool does NOT provide legal advice."
    " Case analysis is based on keyword matching and may be incomplete or inaccurate."
    " Always consult a qualified legal professional."
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db() -> LegalCodeDatabase:
    return LegalCodeDatabase()


@pytest.fixture()
def analyzer() -> CaseAnalyzer:
    return CaseAnalyzer()


# ---------------------------------------------------------------------------
# LEGAL_DISCLAIMER constant test
# ---------------------------------------------------------------------------


def test_legal_disclaimer_constant_exists() -> None:
    assert LEGAL_DISCLAIMER == DISCLAIMER_TEXT


def test_legal_disclaimer_is_not_empty() -> None:
    assert len(LEGAL_DISCLAIMER) > 10


# ---------------------------------------------------------------------------
# LegalSection model tests
# ---------------------------------------------------------------------------


class TestLegalSection:
    def test_valid_ipc_section(self) -> None:
        section = LegalSection(
            code="IPC",
            section_number="302",
            title="Murder",
            description="Punishment for murder.",
            punishment="Death or life imprisonment",
            bailable=False,
        )
        assert section.code == "IPC"
        assert section.section_number == "302"
        assert section.bailable is False

    def test_valid_bns_section(self) -> None:
        section = LegalSection(
            code="BNS",
            section_number="103",
            title="Murder",
            description="Murder under BNS 2023.",
        )
        assert section.code == "BNS"

    def test_invalid_code_rejected(self) -> None:
        with pytest.raises(ValidationError):
            LegalSection(
                code="INVALID_CODE",
                section_number="1",
                title="Test",
                description="Test",
            )

    def test_punishment_optional(self) -> None:
        section = LegalSection(
            code="IPC",
            section_number="34",
            title="Common intention",
            description="Acts by several persons.",
        )
        assert section.punishment is None

    def test_bailable_optional(self) -> None:
        section = LegalSection(
            code="IPC",
            section_number="34",
            title="Common intention",
            description="Acts by several persons.",
        )
        assert section.bailable is None

    def test_bailable_true(self) -> None:
        section = LegalSection(
            code="IPC",
            section_number="379",
            title="Theft",
            description="Theft provisions.",
            bailable=True,
        )
        assert section.bailable is True

    def test_crpc_code_valid(self) -> None:
        section = LegalSection(
            code="CrPC",
            section_number="156",
            title="Police power",
            description="Police officer's power to investigate cognizable case.",
        )
        assert section.code == "CrPC"

    def test_pocso_code_valid(self) -> None:
        section = LegalSection(
            code="POCSO",
            section_number="4",
            title="Penetrative sexual assault",
            description="Punishment for penetrative sexual assault.",
        )
        assert section.code == "POCSO"


# ---------------------------------------------------------------------------
# LegalMapping model tests
# ---------------------------------------------------------------------------


class TestLegalMapping:
    def test_valid_mapping_replaced(self) -> None:
        mapping = LegalMapping(
            old_code="IPC",
            old_section="302",
            new_code="BNS",
            new_section="103",
            status="replaced",
        )
        assert mapping.status == "replaced"

    def test_valid_mapping_amended(self) -> None:
        mapping = LegalMapping(
            old_code="IPC",
            old_section="304A",
            new_code="BNS",
            new_section="106",
            status="amended",
        )
        assert mapping.status == "amended"

    def test_invalid_status_rejected(self) -> None:
        with pytest.raises(ValidationError):
            LegalMapping(
                old_code="IPC",
                old_section="302",
                new_code="BNS",
                new_section="103",
                status="unknown_status",
            )

    def test_repealed_status_valid(self) -> None:
        mapping = LegalMapping(
            old_code="IPC",
            old_section="377",
            new_code="BNS",
            new_section="0",
            status="repealed",
        )
        assert mapping.status == "repealed"


# ---------------------------------------------------------------------------
# CaseAnalysis model tests
# ---------------------------------------------------------------------------


class TestCaseAnalysis:
    def test_default_disclaimer_is_set(self) -> None:
        analysis = CaseAnalysis(
            case_description="Test case",
            relevant_sections=[],
            summary="Test summary",
        )
        assert analysis.disclaimer == LEGAL_DISCLAIMER

    def test_ipc_to_bns_mapping_defaults_empty(self) -> None:
        analysis = CaseAnalysis(
            case_description="Test case",
            relevant_sections=[],
            summary="Test summary",
        )
        assert analysis.ipc_to_bns_mapping == []

    def test_case_description_preserved(self) -> None:
        desc = "The accused committed murder on the night of 5 March."
        analysis = CaseAnalysis(
            case_description=desc,
            relevant_sections=[],
            summary="Summary here",
        )
        assert analysis.case_description == desc


# ---------------------------------------------------------------------------
# LegalCodeDatabase tests
# ---------------------------------------------------------------------------


class TestLegalCodeDatabase:
    def test_lookup_ipc_302(self, db: LegalCodeDatabase) -> None:
        section = db.lookup_ipc("302")
        assert section is not None
        assert section.title == "Murder"
        assert section.bailable is False

    def test_lookup_ipc_379_theft_bailable(self, db: LegalCodeDatabase) -> None:
        section = db.lookup_ipc("379")
        assert section is not None
        assert section.bailable is True

    def test_lookup_ipc_498A(self, db: LegalCodeDatabase) -> None:
        section = db.lookup_ipc("498A")
        assert section is not None
        assert "cruelty" in section.title.lower()

    def test_lookup_ipc_nonexistent_returns_none(self, db: LegalCodeDatabase) -> None:
        assert db.lookup_ipc("9999") is None

    def test_lookup_ipc_whitespace_stripped(self, db: LegalCodeDatabase) -> None:
        section = db.lookup_ipc("  302  ")
        assert section is not None

    def test_lookup_bns_103(self, db: LegalCodeDatabase) -> None:
        section = db.lookup_bns("103")
        assert section is not None
        assert section.title == "Murder"

    def test_lookup_bns_64_rape(self, db: LegalCodeDatabase) -> None:
        section = db.lookup_bns("64")
        assert section is not None

    def test_lookup_bns_nonexistent_returns_none(self, db: LegalCodeDatabase) -> None:
        assert db.lookup_bns("9999") is None

    def test_map_ipc_to_bns_302(self, db: LegalCodeDatabase) -> None:
        mapping = db.map_ipc_to_bns("302")
        assert mapping is not None
        assert mapping.new_section == "103"
        assert mapping.status == "replaced"

    def test_map_ipc_to_bns_304A_amended(self, db: LegalCodeDatabase) -> None:
        mapping = db.map_ipc_to_bns("304A")
        assert mapping is not None
        assert mapping.status == "amended"

    def test_map_ipc_to_bns_nonexistent_returns_none(self, db: LegalCodeDatabase) -> None:
        assert db.map_ipc_to_bns("9999") is None

    def test_map_ipc_whitespace_stripped(self, db: LegalCodeDatabase) -> None:
        mapping = db.map_ipc_to_bns("  302  ")
        assert mapping is not None

    def test_all_ipc_returns_list(self, db: LegalCodeDatabase) -> None:
        sections = db.all_ipc()
        assert isinstance(sections, list)
        assert len(sections) >= 20

    def test_all_bns_returns_list(self, db: LegalCodeDatabase) -> None:
        sections = db.all_bns()
        assert isinstance(sections, list)
        assert len(sections) >= 20

    def test_all_ipc_sections_have_code_ipc(self, db: LegalCodeDatabase) -> None:
        for section in db.all_ipc():
            assert section.code == "IPC"

    def test_all_bns_sections_have_code_bns(self, db: LegalCodeDatabase) -> None:
        for section in db.all_bns():
            assert section.code == "BNS"

    def test_ipc_murder_punishment(self, db: LegalCodeDatabase) -> None:
        section = db.lookup_ipc("302")
        assert section is not None
        assert section.punishment is not None
        assert "life" in section.punishment.lower() or "death" in section.punishment.lower()

    def test_known_ipc_to_bns_mappings(self, db: LegalCodeDatabase) -> None:
        known_pairs = [
            ("302", "103"),
            ("376", "64"),
            ("379", "303"),
            ("420", "318"),
            ("498A", "85"),
        ]
        for ipc_sec, expected_bns in known_pairs:
            mapping = db.map_ipc_to_bns(ipc_sec)
            assert mapping is not None, f"No mapping found for IPC {ipc_sec}"
            assert mapping.new_section == expected_bns


# ---------------------------------------------------------------------------
# CaseAnalyzer tests
# ---------------------------------------------------------------------------


class TestCaseAnalyzer:
    def test_analyze_returns_case_analysis(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The accused committed theft.")
        assert isinstance(result, CaseAnalysis)

    def test_analyze_disclaimer_always_present(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("Some case description.")
        assert result.disclaimer == LEGAL_DISCLAIMER

    def test_analyze_murder_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The accused killed the victim with a knife.")
        assert len(result.relevant_sections) > 0
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "302" in section_numbers or "103" in section_numbers

    def test_analyze_theft_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The accused was caught stealing a mobile phone.")
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "379" in section_numbers or "303" in section_numbers

    def test_analyze_domestic_violence_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze(
            "The husband subjected the wife to domestic violence and cruelty by husband."
        )
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "498A" in section_numbers or "85" in section_numbers

    def test_analyze_rape_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The accused committed rape against the victim.")
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "376" in section_numbers or "64" in section_numbers

    def test_analyze_kidnapping_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The accused committed kidnapping of the child from the school.")
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "363" in section_numbers or "137" in section_numbers

    def test_analyze_cheating_fraud_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze(
            "The accused cheated the victim by running a scam and fraud scheme."
        )
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "420" in section_numbers or "318" in section_numbers

    def test_analyze_unknown_case_returns_guidance(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("This is a very unusual contract dispute.")
        # Should still return a CaseAnalysis with a meaningful summary
        assert isinstance(result, CaseAnalysis)
        assert len(result.summary) > 20

    def test_analyze_unknown_case_empty_sections(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("This is a very unusual contract dispute between parties.")
        # No strong criminal keyword match → empty sections or summary guides to advocate
        assert isinstance(result.relevant_sections, list)

    def test_analyze_ipc_to_bns_mapping_included(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The accused committed theft and robbery.")
        # IPC→BNS mappings should be populated
        assert isinstance(result.ipc_to_bns_mapping, list)
        assert len(result.ipc_to_bns_mapping) > 0

    def test_analyze_summary_mentions_bns_transition(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The accused was involved in murder of the victim.")
        # Summary should mention BNS replacing IPC
        assert "BNS" in result.summary or "Bharatiya" in result.summary

    def test_analyze_case_description_preserved(self, analyzer: CaseAnalyzer) -> None:
        desc = "The accused committed theft in the dwelling house."
        result = analyzer.analyze(desc)
        assert result.case_description == desc

    def test_analyze_rioting_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze(
            "A mob attacked the police in rioting and mob violence near the town."
        )
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "147" in section_numbers or "191" in section_numbers

    def test_analyze_threat_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze(
            "The accused sent threatening messages and intimidation to the victim."
        )
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "506" in section_numbers or "351" in section_numbers

    def test_analyze_multiple_crimes_in_one_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze(
            "The accused committed theft and assault resulting in grievous hurt."
        )
        assert len(result.relevant_sections) > 2

    def test_analyze_case_insensitive(self, analyzer: CaseAnalyzer) -> None:
        result_lower = analyzer.analyze("theft occurred at the shop.")
        result_upper = analyzer.analyze("THEFT OCCURRED AT THE SHOP.")
        # Both should find theft sections
        assert len(result_lower.relevant_sections) > 0
        assert len(result_upper.relevant_sections) > 0

    def test_analyze_no_duplicate_sections(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze(
            "The accused committed murder, theft, robbery and dacoity."
        )
        section_ids = [
            f"{s.code}-{s.section_number}" for s in result.relevant_sections
        ]
        assert len(section_ids) == len(set(section_ids))

    def test_analyze_hit_and_run_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze("The driver caused a hit and run accident death.")
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "304A" in section_numbers or "106" in section_numbers

    def test_analyze_dowry_death_case(self, analyzer: CaseAnalyzer) -> None:
        result = analyzer.analyze(
            "The woman died due to dowry death within 2 years of marriage."
        )
        section_numbers = [s.section_number for s in result.relevant_sections]
        assert "304B" in section_numbers or "80" in section_numbers


# ---------------------------------------------------------------------------
# Integration: CaseAnalysis disclaimer present in every result
# ---------------------------------------------------------------------------


class TestDisclaimerIntegration:
    def test_disclaimer_in_all_analyses(self, analyzer: CaseAnalyzer) -> None:
        cases = [
            "The accused committed murder.",
            "Theft occurred at the shop.",
            "Domestic cruelty by husband.",
            "An unrelated contractual matter.",
        ]
        for case in cases:
            result = analyzer.analyze(case)
            assert result.disclaimer == LEGAL_DISCLAIMER, (
                f"Disclaimer missing in analysis for: {case}"
            )


# ---------------------------------------------------------------------------
# Hypothesis property-based tests
# ---------------------------------------------------------------------------


@given(description=st.text(min_size=5, max_size=200))
@settings(max_examples=20)
def test_analyze_never_raises(description: str) -> None:
    """CaseAnalyzer.analyze must never raise an exception for arbitrary strings."""
    analyzer = CaseAnalyzer()
    result = analyzer.analyze(description)
    assert isinstance(result, CaseAnalysis)
    assert result.disclaimer == LEGAL_DISCLAIMER


@given(section=st.sampled_from(["302", "376", "379", "420", "498A", "304B", "363"]))
@settings(max_examples=10)
def test_known_ipc_sections_always_found(section: str) -> None:
    db = LegalCodeDatabase()
    result = db.lookup_ipc(section)
    assert result is not None
    assert result.section_number == section
