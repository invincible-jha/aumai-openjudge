# Getting Started with aumai-openjudge

> Indian Legal Code Analyser — IPC/BNS statute mapping and keyword-based case analysis.

**LEGAL DISCLAIMER:** aumai-openjudge does NOT provide legal advice. All analysis is keyword-based
and may be incomplete or incorrect. This tool is for educational and research purposes only.
Always consult a qualified, licensed advocate before taking any legal action.

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Python | 3.11 | Required for modern `typing` features |
| pip | 23.0+ | For editable installs |
| pydantic | v2.x | Automatically installed |
| click | 8.x | Automatically installed |

Optional (for server mode):

| Package | Purpose |
|---|---|
| `uvicorn` | ASGI server for `aumai-openjudge serve` |
| `fastapi` | HTTP API framework |

---

## Installation

### Option 1: Install from PyPI

```bash
pip install aumai-openjudge
```

Verify:

```bash
python -c "from aumai_openjudge.core import CaseAnalyzer; print('OK')"
aumai-openjudge --version
```

### Option 2: Install from Source

```bash
git clone https://github.com/aumai/aumai-openjudge
cd aumai-openjudge
pip install -e .
```

### Option 3: Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

pip install aumai-openjudge
```

### Option 4: With Server Support

```bash
pip install "aumai-openjudge[server]"
# or:
pip install aumai-openjudge uvicorn fastapi
```

---

## Step-by-Step Tutorial

### Step 1: Understand the IPC-to-BNS Transition

Before using the library, it is important to understand the legal context:

India replaced the **Indian Penal Code 1860 (IPC)** with the **Bharatiya Nyaya Sanhita 2023 (BNS)** effective 1 July 2024. Key implications:

- Cases filed **before 1 July 2024** are charged under IPC sections
- Cases filed **on or after 1 July 2024** are charged under BNS sections
- Section numbers changed substantially (e.g. IPC 302 → BNS 103 for murder)
- Some punishments were enhanced (e.g. minimum for rape: 7 years IPC → 10 years BNS)
- Some sections were merged or split

aumai-openjudge provides both IPC and BNS sections and the mapping between them.

---

### Step 2: Browse the Section Database

Start by exploring the section database directly from Python:

```python
from aumai_openjudge.core import LegalCodeDatabase

db = LegalCodeDatabase()

# Count sections
ipc_sections = db.all_ipc()
bns_sections = db.all_bns()
print(f"IPC sections in database: {len(ipc_sections)}")
print(f"BNS sections in database: {len(bns_sections)}")

# Browse IPC sections
print("\nIPC Section Summary:")
for s in ipc_sections:
    bail_str = "Bailable" if s.bailable is True else ("Non-bailable" if s.bailable is False else "N/A")
    print(f"  IPC {s.section_number}: {s.title} [{bail_str}]")
```

---

### Step 3: Look Up a Specific Section

```python
from aumai_openjudge.core import LegalCodeDatabase

db = LegalCodeDatabase()

# Look up a well-known IPC section
section = db.lookup_ipc("302")
print(f"IPC {section.section_number}: {section.title}")
print(f"Description: {section.description}")
print(f"Punishment: {section.punishment}")
print(f"Bailable: {section.bailable}")

# Get the BNS equivalent
mapping = db.map_ipc_to_bns("302")
if mapping:
    print(f"\nBNS equivalent: {mapping.new_code} {mapping.new_section}")
    print(f"Mapping status: {mapping.status}")

    bns_section = db.lookup_bns(mapping.new_section)
    if bns_section:
        print(f"BNS description: {bns_section.description}")
```

---

### Step 4: Analyse a Case Description

This is the primary use case for the library. Write a case description in plain English and let the analyser identify relevant IPC and BNS sections:

```python
from aumai_openjudge.core import CaseAnalyzer

# DISCLAIMER: This does NOT constitute legal advice.
analyzer = CaseAnalyzer()

case_text = """
The accused entered the complainant's home, used criminal force against the victim,
and stole jewellery worth Rs 2 lakh. When the victim resisted, the accused issued
a threat to cause grievous hurt.
"""

analysis = analyzer.analyze(case_text)

# Print summary
print("CASE ANALYSIS SUMMARY")
print("=" * 55)
print(analysis.summary)

# Print matched sections
print("\nRELEVANT SECTIONS:")
for section in analysis.relevant_sections:
    bail_str = "Bailable" if section.bailable is True else "Non-bailable"
    print(f"\n  {section.code} {section.section_number}: {section.title}")
    print(f"  Punishment: {section.punishment}")
    print(f"  Status: {bail_str}")

# Print IPC-to-BNS mappings
print("\nIPC TO BNS CROSS-REFERENCE (BNS effective 1 July 2024):")
for m in analysis.ipc_to_bns_mapping:
    print(f"  {m['ipc']} -> {m['bns']} ({m['status']})")

# ALWAYS print the disclaimer
print(f"\n{'*' * 55}")
print("DISCLAIMER:", analysis.disclaimer)
print("*" * 55)
```

---

### Step 5: Handle Edge Cases

```python
from aumai_openjudge.core import CaseAnalyzer

analyzer = CaseAnalyzer()

# Case with no matching keywords (civil, contractual, family dispute)
analysis = analyzer.analyze(
    "The landlord refuses to return the security deposit after lease termination."
)

print("Sections matched:", len(analysis.relevant_sections))
print("Summary:", analysis.summary)
# Output will note that no criminal sections matched and advise consultation

# Case with overlapping keywords (multiple offences)
analysis2 = analyzer.analyze(
    "The gang robbed the shop, threatened the owner, and caused grievous hurt to a staff member."
)
print(f"\nMultiple offences — {len(analysis2.relevant_sections)} sections matched")
```

---

### Step 6: Serialise Analysis to JSON

```python
from aumai_openjudge.core import CaseAnalyzer
import json

analyzer = CaseAnalyzer()
analysis = analyzer.analyze("The accused committed cheating and criminal breach of trust.")

# Full Pydantic serialisation
output_dict = analysis.model_dump()
output_json = analysis.model_dump_json(indent=2)

# Store to file
with open("case_analysis.json", "w", encoding="utf-8") as f:
    f.write(output_json)

# Parse back
from aumai_openjudge.models import CaseAnalysis
restored = CaseAnalysis.model_validate(json.loads(output_json))
assert restored.disclaimer == analysis.disclaimer
```

---

## Common Patterns and Recipes

### Pattern 1: Batch-Analyse Multiple Case Descriptions

```python
from aumai_openjudge.core import CaseAnalyzer

analyzer = CaseAnalyzer()

cases = [
    "Murder committed with premeditation during a robbery.",
    "Domestic violence and dowry harassment over three years.",
    "Rash driving caused death. Driver fled the scene.",
    "Online fraud and cheating via fake investment scheme.",
]

for i, case_text in enumerate(cases, 1):
    analysis = analyzer.analyze(case_text)
    ipc_nums = [s.section_number for s in analysis.relevant_sections if s.code == "IPC"]
    bns_nums = [s.section_number for s in analysis.relevant_sections if s.code == "BNS"]
    print(f"\nCase {i}:")
    print(f"  IPC: {', '.join(ipc_nums) or 'none matched'}")
    print(f"  BNS: {', '.join(bns_nums) or 'none matched'}")
```

---

### Pattern 2: Find the BNS Equivalent for Any IPC Section

```python
from aumai_openjudge.core import LegalCodeDatabase

db = LegalCodeDatabase()

ipc_sections_of_interest = ["302", "376", "498A", "304B", "420", "304A"]

print("IPC to BNS cross-reference table:")
print(f"{'IPC Section':<14} {'IPC Title':<40} {'BNS':<10} Status")
print("-" * 72)

for ipc_num in ipc_sections_of_interest:
    ipc_section = db.lookup_ipc(ipc_num)
    mapping = db.map_ipc_to_bns(ipc_num)
    if ipc_section and mapping:
        print(
            f"IPC {ipc_num:<10} {ipc_section.title:<40} "
            f"BNS {mapping.new_section:<6} {mapping.status}"
        )
```

---

### Pattern 3: Filter Non-Bailable Sections from an Analysis

```python
from aumai_openjudge.core import CaseAnalyzer

analyzer = CaseAnalyzer()
analysis = analyzer.analyze(
    "Kidnapping, robbery, and criminal conspiracy by an organised group."
)

bailable = [s for s in analysis.relevant_sections if s.bailable is True]
non_bailable = [s for s in analysis.relevant_sections if s.bailable is False]

print(f"Non-bailable offences ({len(non_bailable)}):")
for s in non_bailable:
    print(f"  {s.code} {s.section_number}: {s.title}")

print(f"\nBailable offences ({len(bailable)}):")
for s in bailable:
    print(f"  {s.code} {s.section_number}: {s.title}")
```

---

### Pattern 4: Build a Simple Section Cross-Reference Report

```python
from aumai_openjudge.core import LegalCodeDatabase
import json

db = LegalCodeDatabase()

# Build a complete cross-reference report for all mapped sections
report = []
for ipc_section in db.all_ipc():
    mapping = db.map_ipc_to_bns(ipc_section.section_number)
    entry = {
        "ipc_section": ipc_section.section_number,
        "ipc_title": ipc_section.title,
        "ipc_punishment": ipc_section.punishment,
        "ipc_bailable": ipc_section.bailable,
        "bns_section": mapping.new_section if mapping else None,
        "mapping_status": mapping.status if mapping else None,
    }
    if mapping:
        bns_sec = db.lookup_bns(mapping.new_section)
        if bns_sec:
            entry["bns_punishment"] = bns_sec.punishment
    report.append(entry)

print(json.dumps(report[:3], indent=2, ensure_ascii=False))
```

---

### Pattern 5: Integrate with a Larger Analysis Pipeline

```python
from aumai_openjudge.core import CaseAnalyzer
from aumai_openjudge.models import CaseAnalysis

def enrich_case_for_legal_aid(case_description: str, case_id: str) -> dict:
    """
    Wrapper for use in a legal aid system pipeline.
    Returns a structured dict safe for API responses.
    DOES NOT provide legal advice.
    """
    analyzer = CaseAnalyzer()
    analysis: CaseAnalysis = analyzer.analyze(case_description)

    return {
        "case_id": case_id,
        "disclaimer": analysis.disclaimer,  # Always included
        "summary": analysis.summary,
        "ipc_sections": [
            {"number": s.section_number, "title": s.title, "bailable": s.bailable}
            for s in analysis.relevant_sections
            if s.code == "IPC"
        ],
        "bns_sections": [
            {"number": s.section_number, "title": s.title}
            for s in analysis.relevant_sections
            if s.code == "BNS"
        ],
        "ipc_to_bns": analysis.ipc_to_bns_mapping,
    }

result = enrich_case_for_legal_aid(
    "The accused harassed the victim and caused hurt.",
    case_id="CASE-2024-001"
)
import json
print(json.dumps(result, indent=2))
```

---

## Troubleshooting FAQ

**Q: The analysis returns no sections for a case that clearly involves criminal offences.**

The keyword matching engine uses substring matching against a fixed vocabulary of ~100 keywords. If your case description uses uncommon wording or very formal/legalistic language, keywords may not match. Try rephrasing with common terms: "murder", "theft", "cheating", "kidnapping", "assault", etc.

---

**Q: The analysis returns sections that do not seem relevant to the case.**

This is expected behaviour of keyword matching. The engine may match sections based on incidental word overlap. For example, a description mentioning "blocked" may trigger the "wrongful restraint" section even if the context is not criminal restraint. All outputs include a mandatory disclaimer precisely because of this limitation.

---

**Q: I need to analyse cases under POCSO, IT Act, SC/ST Act, or NDPS Act.**

These special statutes are not currently in the database. The library covers the 30 most commonly invoked IPC sections and their BNS equivalents. Contributions adding special statute coverage are very welcome.

---

**Q: I looked up IPC 302 but `lookup_bns("302")` returns data about stolen property, not murder.**

This is correct and intentional. BNS 302 corresponds to "Dishonestly receiving stolen property" (formerly IPC 411). BNS 103 corresponds to murder (formerly IPC 302). The section numbers changed completely in the BNS transition — use `map_ipc_to_bns()` to find the correct BNS number for any IPC section, then use `lookup_bns()` with the result.

---

**Q: `aumai-openjudge serve` fails with "No module named uvicorn".**

Install uvicorn: `pip install uvicorn`. For production deployments also install `fastapi`.

---

**Q: Can I use this output in court or to prepare an FIR?**

No. This tool is for educational and research purposes only and does not provide legal advice. Output should never be used as a basis for legal action without verification by a qualified, licensed advocate. See the full legal disclaimer.

---

**Q: The BNS section numbers in my reference material do not match the database.**

The BNS numbering in this library follows the Bharatiya Nyaya Sanhita 2023 as enacted and in force from 1 July 2024. Discrepancies may exist with draft versions or unofficial summaries. If you find an error, please open an issue with the relevant gazette citation.
