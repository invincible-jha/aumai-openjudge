# API Reference — aumai-openjudge

> Indian Legal Code Analyser — IPC/BNS statute mapping and case analysis.

**Package:** `aumai_openjudge`
**Version:** 0.1.0
**Python:** 3.11+

**LEGAL DISCLAIMER:** This library does NOT provide legal advice. All analysis is keyword-based and
educational in nature. Always consult a qualified advocate.

---

## Module: `aumai_openjudge.core`

Core business logic. Contains two classes: `LegalCodeDatabase` and `CaseAnalyzer`.

---

### class `LegalCodeDatabase`

In-memory database of IPC sections, BNS sections, and the IPC-to-BNS mapping table. Provides lookup by section number and cross-reference between the two codes.

```python
from aumai_openjudge.core import LegalCodeDatabase
```

#### Constructor

```python
LegalCodeDatabase() -> LegalCodeDatabase
```

Initialises the database from the built-in `_IPC_SECTIONS`, `_BNS_SECTIONS`, and `_IPC_TO_BNS_MAPPINGS` lists. No arguments required.

**Example:**

```python
db = LegalCodeDatabase()
```

---

#### `LegalCodeDatabase.lookup_ipc()`

```python
def lookup_ipc(self, section: str) -> LegalSection | None
```

Look up an IPC section by its section number string.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `section` | `str` | IPC section number, e.g. `"302"`, `"498A"`, `"304B"` |

**Returns:** `LegalSection` if found, `None` if not in the database.

**Notes:** Leading/trailing whitespace is stripped automatically. The database covers 30 IPC sections.

**Raises:** Nothing.

**Example:**

```python
db = LegalCodeDatabase()

ipc_498a = db.lookup_ipc("498A")
if ipc_498a:
    print(ipc_498a.title)         # "Cruelty by husband or relatives"
    print(ipc_498a.punishment)    # "Imprisonment up to 3 years and fine"
    print(ipc_498a.bailable)      # False

# Whitespace is handled
same = db.lookup_ipc("  302  ")
assert same is not None

# Non-existent section
assert db.lookup_ipc("999") is None
```

---

#### `LegalCodeDatabase.lookup_bns()`

```python
def lookup_bns(self, section: str) -> LegalSection | None
```

Look up a BNS (Bharatiya Nyaya Sanhita 2023) section by its section number string.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `section` | `str` | BNS section number, e.g. `"103"`, `"64"`, `"3(5)"` |

**Returns:** `LegalSection` if found, `None` if not in the database.

**Notes:** The BNS section numbers are completely different from IPC section numbers. Use `map_ipc_to_bns()` to find the correct BNS number for a given IPC section.

**Raises:** Nothing.

**Example:**

```python
db = LegalCodeDatabase()

# BNS 103 = Murder (formerly IPC 302)
bns_103 = db.lookup_bns("103")
print(bns_103.title)       # "Murder"
print(bns_103.punishment)  # "Death or imprisonment for life and fine"

# BNS 302 = Receiving stolen property (NOT murder)
bns_302 = db.lookup_bns("302")
print(bns_302.title)  # "Dishonestly receiving stolen property"
```

**Important:** BNS 302 is NOT the BNS equivalent of IPC 302. The mapping is IPC 302 → BNS 103. Always use `map_ipc_to_bns()` for cross-referencing.

---

#### `LegalCodeDatabase.map_ipc_to_bns()`

```python
def map_ipc_to_bns(self, ipc_section: str) -> LegalMapping | None
```

Get the BNS equivalent mapping for a given IPC section number.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `ipc_section` | `str` | IPC section number, e.g. `"302"`, `"376"`, `"498A"` |

**Returns:** `LegalMapping` if a mapping exists for the given IPC section, `None` if not mapped (e.g. for sections without BNS equivalents or sections not in the database).

**Raises:** Nothing.

**Example:**

```python
db = LegalCodeDatabase()

mapping = db.map_ipc_to_bns("376")
if mapping:
    print(f"IPC {mapping.old_section} -> {mapping.new_code} {mapping.new_section}")
    print(f"Status: {mapping.status}")
    # "IPC 376 -> BNS 64"
    # "Status: replaced"

    # Fetch the actual BNS section
    bns_sec = db.lookup_bns(mapping.new_section)
    print(bns_sec.punishment)
    # "Minimum 10 years (from 7 under IPC), may extend to life"
```

---

#### `LegalCodeDatabase.all_ipc()`

```python
def all_ipc(self) -> list[LegalSection]
```

Return all IPC sections in the database.

**Returns:** `list[LegalSection]` — All 30 IPC sections. Order is not guaranteed to match insertion order.

**Raises:** Nothing.

**Example:**

```python
db = LegalCodeDatabase()
all_ipc = db.all_ipc()
print(f"Total IPC sections: {len(all_ipc)}")

non_bailable = [s for s in all_ipc if s.bailable is False]
print(f"Non-bailable: {len(non_bailable)}")
```

---

#### `LegalCodeDatabase.all_bns()`

```python
def all_bns(self) -> list[LegalSection]
```

Return all BNS sections in the database.

**Returns:** `list[LegalSection]` — All 28 BNS sections.

**Raises:** Nothing.

**Example:**

```python
db = LegalCodeDatabase()
all_bns = db.all_bns()
print(f"Total BNS sections: {len(all_bns)}")
```

---

### class `CaseAnalyzer`

Analyses case descriptions against Indian criminal law through keyword matching.

```python
from aumai_openjudge.core import CaseAnalyzer
```

#### Constructor

```python
CaseAnalyzer() -> CaseAnalyzer
```

Creates a `CaseAnalyzer` with its own internal `LegalCodeDatabase`. No arguments required.

**Example:**

```python
analyzer = CaseAnalyzer()
```

---

#### `CaseAnalyzer.analyze()`

```python
def analyze(self, case_description: str) -> CaseAnalysis
```

Perform keyword-based legal analysis on a case description string.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `case_description` | `str` | Plain English case description. Case-insensitive. No minimum or maximum length enforced. |

**Returns:** `CaseAnalysis` — A validated Pydantic model containing:
- `relevant_sections`: list of matched `LegalSection` objects (both IPC and BNS)
- `ipc_to_bns_mapping`: list of mapping dicts for all matched IPC sections
- `summary`: human-readable analysis summary string
- `disclaimer`: mandatory legal disclaimer string (always populated)

**Raises:** Nothing. If no keywords match, a `CaseAnalysis` is still returned with an empty `relevant_sections` list and a summary advising professional consultation.

**Matching algorithm:**

1. Case description is lowercased
2. Each of the 27 keyword groups in `_KEYWORD_SECTION_MAP` is tested for any keyword substring match
3. All matching IPC and BNS `LegalSection` objects are fetched and deduplicated
4. For each matched IPC section, the `LegalMapping` is fetched and added to `ipc_to_bns_mapping`
5. The summary includes matched offence categories, IPC section numbers, and BNS section numbers
6. BNS transition note (effective 1 July 2024) is appended to the summary when sections are matched

**Example:**

```python
from aumai_openjudge.core import CaseAnalyzer

# DISCLAIMER: For educational use only. Not legal advice.
analyzer = CaseAnalyzer()

analysis = analyzer.analyze(
    "The accused and his associates committed robbery and threatened the victims."
)

# Access summary
print(analysis.summary)

# Access matched sections
for s in analysis.relevant_sections:
    print(f"  {s.code} {s.section_number}: {s.title}")

# Access IPC-to-BNS mappings
for m in analysis.ipc_to_bns_mapping:
    print(f"  {m['ipc']} -> {m['bns']} ({m['status']})")

# Disclaimer is always present
assert "does NOT provide legal advice" in analysis.disclaimer

# Empty case
empty = analyzer.analyze("The parties had a business disagreement about invoice terms.")
assert len(empty.relevant_sections) == 0
assert "Consult a qualified advocate" in empty.summary
```

**Keyword coverage groups (27 total):**

| Category | Example Keywords |
|---|---|
| murder | murder, killed, death, homicide |
| attempt to murder | attempt to murder, attempted murder |
| culpable homicide | culpable homicide, manslaughter |
| rape | rape, sexual assault |
| theft | theft, stealing, stolen |
| dwelling theft | dwelling, house theft, home theft |
| robbery | robbery, snatching |
| dacoity | dacoity, gang robbery, armed robbery |
| cheating | cheating, fraud, deception, scam |
| criminal breach of trust | breach of trust, misappropriation |
| domestic cruelty | domestic violence, cruelty by husband, marital cruelty |
| dowry death | dowry death, dowry harassment, dowry murder |
| kidnapping | kidnapping, abduction, missing child |
| assault on modesty | molestation, outrage modesty, eve teasing physical |
| causing hurt | hurt, beating, assault, punch, attack person |
| grievous hurt | grievous hurt, severe injury, permanent injury |
| wrongful restraint | wrongful restraint, confined, blocked path |
| criminal intimidation | threat, intimidation, threatening |
| criminal conspiracy | conspiracy, planning crime, gang plan |
| rioting | rioting, mob violence, unlawful assembly |
| promoting enmity | communal tension, religious hatred, caste violence |
| receiving stolen property | receiving stolen, buying stolen |
| false evidence | false evidence, perjury, false witness |
| criminal trespass | trespass, breaking in, unlawful entry |
| rash driving | rash driving, dangerous driving, road accident negligence |
| death by negligence | negligence death, accident death, hit and run |
| insulting woman's modesty | eve teasing, gesture insult woman, verbal harassment woman |

---

## Module: `aumai_openjudge.models`

Pydantic v2 data models for legal data. All models enforce strict validation.

```python
from aumai_openjudge.models import LegalSection, CaseAnalysis, LegalMapping, LEGAL_DISCLAIMER
```

---

### constant `LEGAL_DISCLAIMER`

```python
LEGAL_DISCLAIMER: str = (
    "This tool does NOT provide legal advice."
    " Case analysis is based on keyword matching and may be incomplete or inaccurate."
    " Always consult a qualified legal professional."
)
```

The mandatory disclaimer string attached to every `CaseAnalysis` output. Also available from `aumai_openjudge.models`.

---

### class `LegalSection`

A single provision of Indian law (IPC, BNS, CrPC, or BNSS).

```python
class LegalSection(BaseModel):
    code: str           # pattern: ^(IPC|BNS|CrPC|BNSS|IT Act|POCSO)$
    section_number: str
    title: str
    description: str
    punishment: str | None = None
    bailable: bool | None = None
```

#### Fields

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `code` | `str` | Yes | Must match `^(IPC\|BNS\|CrPC\|BNSS\|IT Act\|POCSO)$` | Legal code identifier |
| `section_number` | `str` | Yes | — | Section number string, e.g. `"302"`, `"498A"`, `"3(5)"` |
| `title` | `str` | Yes | — | Short descriptive title of the provision |
| `description` | `str` | Yes | — | Full text description of the section |
| `punishment` | `str \| None` | No | — | Prescribed punishment as a human-readable string; `None` if not applicable |
| `bailable` | `bool \| None` | No | — | `True` if bailable offence, `False` if non-bailable, `None` if not applicable (e.g. general provisions) |

**Valid `code` values:** `IPC`, `BNS`, `CrPC`, `BNSS`, `IT Act`, `POCSO`

**Example:**

```python
from aumai_openjudge.models import LegalSection

section = LegalSection(
    code="IPC",
    section_number="302",
    title="Murder",
    description="Whoever commits murder shall be punished...",
    punishment="Death or life imprisonment and fine",
    bailable=False,
)

print(section.model_dump_json(indent=2))
```

**Validation errors:**

```python
from pydantic import ValidationError

try:
    bad = LegalSection(
        code="INVALID_CODE",  # Fails regex validation
        section_number="302",
        title="Test",
        description="Test",
    )
except ValidationError as exc:
    print(exc)
    # String should match pattern '^(IPC|BNS|...)$'
```

---

### class `CaseAnalysis`

The complete result of a case analysis operation. Always includes a disclaimer.

```python
class CaseAnalysis(BaseModel):
    case_description: str
    relevant_sections: list[LegalSection]
    ipc_to_bns_mapping: list[dict[str, object]] = []
    summary: str
    disclaimer: str = LEGAL_DISCLAIMER
```

#### Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `case_description` | `str` | Yes | — | The original case description text passed to `analyze()` |
| `relevant_sections` | `list[LegalSection]` | Yes | — | All matched IPC and BNS `LegalSection` objects (deduplicated) |
| `ipc_to_bns_mapping` | `list[dict[str, object]]` | No | `[]` | Each dict has keys `"ipc"` (str), `"bns"` (str), `"status"` (str) |
| `summary` | `str` | Yes | — | Human-readable narrative summarising the analysis |
| `disclaimer` | `str` | No | `LEGAL_DISCLAIMER` | Mandatory legal disclaimer; always populated |

**The `ipc_to_bns_mapping` dict structure:**

```python
{
    "ipc": "IPC 302",       # e.g. "IPC 302"
    "bns": "BNS 103",       # e.g. "BNS 103"
    "status": "replaced",   # "replaced", "amended", or "repealed"
}
```

**Example:**

```python
from aumai_openjudge.core import CaseAnalyzer

analyzer = CaseAnalyzer()
analysis = analyzer.analyze("Murder and robbery with criminal conspiracy.")

# Type-safe access
for section in analysis.relevant_sections:
    assert isinstance(section.bailable, (bool, type(None)))

# Serialisation
json_str = analysis.model_dump_json(indent=2)

# Always check disclaimer
assert len(analysis.disclaimer) > 0
```

---

### class `LegalMapping`

Mapping between an old Indian Penal Code (or CrPC) section and its new BNS (or BNSS) equivalent.

```python
class LegalMapping(BaseModel):
    old_code: str     # "IPC" or "CrPC"
    old_section: str
    new_code: str     # "BNS" or "BNSS"
    new_section: str
    status: str       # pattern: ^(replaced|amended|repealed)$
```

#### Fields

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `old_code` | `str` | Yes | — | Old code name: `"IPC"` or `"CrPC"` |
| `old_section` | `str` | Yes | — | Old section number |
| `new_code` | `str` | Yes | — | New code name: `"BNS"` or `"BNSS"` |
| `new_section` | `str` | Yes | — | New section number in the replacement code |
| `status` | `str` | Yes | Must match `^(replaced\|amended\|repealed)$` | Nature of the change |

**Status values:**

| Value | Meaning |
|---|---|
| `replaced` | The old section was removed and a new section with similar content was added under a new number |
| `amended` | The old section's content was modified in the new code (e.g. enhanced punishment) |
| `repealed` | The old section was removed without a direct equivalent |

**Example:**

```python
from aumai_openjudge.core import LegalCodeDatabase

db = LegalCodeDatabase()
mapping = db.map_ipc_to_bns("304A")

print(mapping.old_code)    # "IPC"
print(mapping.old_section) # "304A"
print(mapping.new_code)    # "BNS"
print(mapping.new_section) # "106"
print(mapping.status)      # "amended" — punishment enhanced for hit-and-run
```

---

## Module: `aumai_openjudge` (package root)

```python
import aumai_openjudge
print(aumai_openjudge.__version__)  # "0.1.0"
```

All classes are imported directly from `aumai_openjudge.core` and `aumai_openjudge.models`.

---

## CLI Reference (Programmatic)

The Click CLI can be invoked from Python for testing:

```python
from click.testing import CliRunner
from aumai_openjudge.cli import main

runner = CliRunner()
result = runner.invoke(main, ["--version"])
print(result.output)
assert result.exit_code == 0
```

---

## Constants

### `aumai_openjudge.models.LEGAL_DISCLAIMER`

```python
LEGAL_DISCLAIMER = (
    "This tool does NOT provide legal advice."
    " Case analysis is based on keyword matching and may be incomplete or inaccurate."
    " Always consult a qualified legal professional."
)
```

This constant is imported by both `models.py` and `cli.py`. It is embedded in every `CaseAnalysis` object returned by `CaseAnalyzer.analyze()`. Consumer code should always surface this disclaimer to end users.

---

## Error Handling

aumai-openjudge uses Pydantic v2 for all data model validation. The public API methods (`lookup_ipc`, `lookup_bns`, `map_ipc_to_bns`, `analyze`) do not raise exceptions under normal usage — they return `None` or empty structures for unmatched inputs.

The `LegalSection` model validates the `code` field against a regex pattern. Attempting to construct a `LegalSection` with an invalid code will raise `pydantic.ValidationError`.

The `LegalMapping` model validates the `status` field against `^(replaced|amended|repealed)$`. Invalid status values will raise `pydantic.ValidationError`.

**Common validation errors:**

| Error | Cause | Fix |
|---|---|---|
| `String should match pattern '...'` on `code` | Unknown legal code string | Use `IPC`, `BNS`, `CrPC`, `BNSS`, `IT Act`, or `POCSO` |
| `String should match pattern '...'` on `status` | Unknown mapping status | Use `replaced`, `amended`, or `repealed` |
| `Field required` | Missing required field | Check all required fields are provided |
