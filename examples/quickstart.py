"""aumai-openjudge quickstart — IPC/BNS legal code analysis demonstrations.

DISCLAIMER: This tool does NOT provide legal advice.
Case analysis is based on keyword matching and may be incomplete or
inaccurate.  Always consult a qualified legal professional for any
matter with legal implications.

This file demonstrates:
  1. Looking up a specific IPC section by number.
  2. Looking up the BNS 2023 equivalent section.
  3. Mapping IPC sections to their BNS replacements in bulk.
  4. Analysing a single-offence case description (robbery).
  5. Analysing a multi-offence case with overlapping charge categories.

Run directly:
    python examples/quickstart.py

Install first:
    pip install aumai-openjudge
"""

from __future__ import annotations

from aumai_openjudge.core import CaseAnalyzer, LegalCodeDatabase
from aumai_openjudge.models import LEGAL_DISCLAIMER, CaseAnalysis, LegalSection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_section(section: LegalSection) -> None:
    """Print a compact summary of a single LegalSection."""
    bailable_label = (
        "bailable" if section.bailable is True
        else "non-bailable" if section.bailable is False
        else "see statute"
    )
    print(f"    {section.code} {section.section_number}: {section.title}")
    print(f"      Punishment : {section.punishment or 'See description'}")
    print(f"      Bailable   : {bailable_label}")


def _print_analysis(analysis: CaseAnalysis) -> None:
    """Print a structured summary of a CaseAnalysis result."""
    print(f"\n  Summary:\n    {analysis.summary}")

    section_count = len(analysis.relevant_sections)
    print(f"\n  Relevant sections ({section_count}) — showing up to 6:")
    for section in analysis.relevant_sections[:6]:
        _print_section(section)

    if analysis.ipc_to_bns_mapping:
        print("\n  IPC -> BNS transition mappings:")
        for mapping in analysis.ipc_to_bns_mapping:
            print(
                f"    {mapping['ipc']}  ->  {mapping['bns']}  "
                f"[status: {mapping['status']}]"
            )

    print(f"\n  Disclaimer: {analysis.disclaimer}")


# ---------------------------------------------------------------------------
# Demo 1: Direct IPC section lookup
# ---------------------------------------------------------------------------

def demo_ipc_lookup() -> None:
    """Look up IPC sections 302, 420, and 498A by their section numbers.

    LegalCodeDatabase.lookup_ipc() returns None when a section number is
    absent from the database — always handle None in production code.
    """
    print("\n--- Demo 1: IPC Section Lookup ---")

    db = LegalCodeDatabase()

    for section_number in ["302", "420", "498A"]:
        section = db.lookup_ipc(section_number)
        if section is None:
            print(f"  IPC {section_number}: not in database")
            continue
        print(f"\n  IPC {section_number}:")
        _print_section(section)


# ---------------------------------------------------------------------------
# Demo 2: BNS 2023 section lookup
# ---------------------------------------------------------------------------

def demo_bns_lookup() -> None:
    """Look up BNS 2023 sections corresponding to the IPC sections in Demo 1.

    The Bharatiya Nyaya Sanhita (BNS) replaced the IPC from 1 July 2024.
    FIRs registered after that date are filed under BNS section numbers.
    """
    print("\n--- Demo 2: BNS 2023 Section Lookup ---")

    db = LegalCodeDatabase()

    # BNS equivalents: IPC 302 -> BNS 103, IPC 420 -> BNS 318, IPC 498A -> BNS 85
    for section_number in ["103", "318", "85"]:
        section = db.lookup_bns(section_number)
        if section is None:
            print(f"  BNS {section_number}: not in database")
            continue
        print(f"\n  BNS {section_number}:")
        _print_section(section)


# ---------------------------------------------------------------------------
# Demo 3: Bulk IPC-to-BNS mapping
# ---------------------------------------------------------------------------

def demo_ipc_to_bns_mapping() -> None:
    """Map a set of IPC sections to their BNS equivalents in one pass.

    LegalCodeDatabase.map_ipc_to_bns() returns a LegalMapping with
    old_section, new_section, and status ('replaced', 'amended', 'repealed').
    Returns None when no mapping is recorded.
    """
    print("\n--- Demo 3: Bulk IPC-to-BNS Mapping ---")

    db = LegalCodeDatabase()

    ipc_sections = ["302", "376", "304A", "420", "498A", "506"]

    print(f"  {'IPC':>6}  ->  {'BNS':<6}  Status")
    print(f"  {'-'*6}  --  {'-'*6}  {'-'*10}")

    for ipc_number in ipc_sections:
        mapping = db.map_ipc_to_bns(ipc_number)
        if mapping is None:
            print(f"  {ipc_number:>6}       (no BNS mapping recorded)")
        else:
            print(
                f"  {mapping.old_section:>6}  ->  {mapping.new_section:<6}  "
                f"{mapping.status}"
            )


# ---------------------------------------------------------------------------
# Demo 4: Single-offence case analysis
# ---------------------------------------------------------------------------

def demo_single_offence_analysis() -> None:
    """Analyse a robbery case description using keyword-based section matching.

    CaseAnalyzer.analyze() returns both legacy IPC and current BNS 2023
    sections, plus a plain-English summary and the mandatory disclaimer.
    """
    print("\n--- Demo 4: Single-Offence Case Analysis (Robbery) ---")

    analyzer = CaseAnalyzer()

    case_description = (
        "On the night of 15 February 2026, the accused allegedly snatched "
        "a mobile phone and wallet from the complainant at knifepoint near "
        "Sector 14, Gurugram.  The complainant sustained minor injuries. "
        "Three witnesses have provided statements to the police."
    )

    print(f"  Case: {case_description[:110]}...")
    analysis = analyzer.analyze(case_description)
    _print_analysis(analysis)


# ---------------------------------------------------------------------------
# Demo 5: Multi-offence case analysis
# ---------------------------------------------------------------------------

def demo_multi_offence_analysis() -> None:
    """Analyse a complex case spanning multiple overlapping offence categories.

    When the description contains keywords for several offences, the analyzer
    surfaces all matching IPC and BNS sections so that counsel can review
    which charges to frame.
    """
    print("\n--- Demo 5: Multi-Offence Case Analysis ---")

    analyzer = CaseAnalyzer()

    case_description = (
        "The complainant alleges that her husband and his relatives subjected "
        "her to domestic violence and cruelty over two years, making repeated "
        "threats and intimidation related to dowry demands.  She was also "
        "wrongfully confined to the marital home for three days and was "
        "unable to contact her family.  A dowry harassment complaint was "
        "registered at the local police station."
    )

    print(f"  Case: {case_description[:110]}...")
    analysis = analyzer.analyze(case_description)
    _print_analysis(analysis)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run all five openjudge quickstart demonstrations."""
    print("=" * 60)
    print("aumai-openjudge quickstart")
    print("IPC/BNS legal code database and case analyser")
    print("=" * 60)
    print(f"\nDISCLAIMER: {LEGAL_DISCLAIMER}\n")

    demo_ipc_lookup()
    demo_bns_lookup()
    demo_ipc_to_bns_mapping()
    demo_single_offence_analysis()
    demo_multi_offence_analysis()

    print("\nDone.")


if __name__ == "__main__":
    main()
