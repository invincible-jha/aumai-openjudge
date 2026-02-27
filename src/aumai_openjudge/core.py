"""Core logic for aumai-openjudge: IPC/BNS legal code database and case analyser."""

from __future__ import annotations

from .models import LEGAL_DISCLAIMER, CaseAnalysis, LegalMapping, LegalSection

__all__ = ["LegalCodeDatabase", "CaseAnalyzer"]

# ---------------------------------------------------------------------------
# Top 50 IPC sections and their BNS equivalents (as of Bharatiya Nyaya Sanhita 2023)
# ---------------------------------------------------------------------------

_IPC_SECTIONS: list[dict[str, object]] = [
    {"code": "IPC", "section_number": "302", "title": "Murder", "description": "Punishment for murder. Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.", "punishment": "Death or life imprisonment and fine", "bailable": False},
    {"code": "IPC", "section_number": "307", "title": "Attempt to murder", "description": "Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished.", "punishment": "Imprisonment up to 10 years, or life if hurt caused", "bailable": False},
    {"code": "IPC", "section_number": "304", "title": "Culpable homicide not amounting to murder", "description": "Whoever commits culpable homicide not amounting to murder shall be punished.", "punishment": "Imprisonment for life or up to 10 years", "bailable": False},
    {"code": "IPC", "section_number": "376", "title": "Rape", "description": "Punishment for rape. Not less than 7 years which may extend to imprisonment for life.", "punishment": "Minimum 7 years, may extend to life imprisonment", "bailable": False},
    {"code": "IPC", "section_number": "379", "title": "Theft", "description": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": True},
    {"code": "IPC", "section_number": "380", "title": "Theft in dwelling house", "description": "Whoever commits theft in any building, tent or vessel, which building, tent or vessel is used as a human dwelling, shall be punished.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "IPC", "section_number": "392", "title": "Robbery", "description": "Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.", "punishment": "Rigorous imprisonment up to 10 years and fine", "bailable": False},
    {"code": "IPC", "section_number": "395", "title": "Dacoity", "description": "Whoever commits dacoity shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years.", "punishment": "Life imprisonment or rigorous imprisonment up to 10 years", "bailable": False},
    {"code": "IPC", "section_number": "420", "title": "Cheating and dishonestly inducing delivery of property", "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person shall be punished.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "IPC", "section_number": "406", "title": "Criminal breach of trust", "description": "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": False},
    {"code": "IPC", "section_number": "498A", "title": "Cruelty by husband or relatives", "description": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished.", "punishment": "Imprisonment up to 3 years and fine", "bailable": False},
    {"code": "IPC", "section_number": "304B", "title": "Dowry death", "description": "Where the death of a woman is caused by burns or bodily injury in unnatural circumstances within 7 years of marriage and there is cruelty or harassment for dowry.", "punishment": "Minimum 7 years, may extend to life imprisonment", "bailable": False},
    {"code": "IPC", "section_number": "363", "title": "Kidnapping", "description": "Whoever kidnaps any person from India or from lawful guardianship shall be punished.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "IPC", "section_number": "354", "title": "Assault or criminal force on woman to outrage modesty", "description": "Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely to outrage her modesty, shall be punished.", "punishment": "Minimum 1 year, may extend to 5 years and fine", "bailable": False},
    {"code": "IPC", "section_number": "323", "title": "Voluntarily causing hurt", "description": "Whoever voluntarily causes hurt shall be punished with imprisonment for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.", "punishment": "Imprisonment up to 1 year, or fine up to Rs 1000, or both", "bailable": True},
    {"code": "IPC", "section_number": "325", "title": "Voluntarily causing grievous hurt", "description": "Whoever voluntarily causes grievous hurt shall be punished with imprisonment for a term which may extend to seven years, and shall also be liable to fine.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "IPC", "section_number": "341", "title": "Wrongful restraint", "description": "Whoever wrongfully restrains any person shall be punished with simple imprisonment for a term which may extend to one month, or with fine which may extend to five hundred rupees.", "punishment": "Simple imprisonment up to 1 month, or fine up to Rs 500", "bailable": True},
    {"code": "IPC", "section_number": "506", "title": "Criminal intimidation", "description": "Whoever commits the offence of criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.", "punishment": "Imprisonment up to 2 years, or fine, or both", "bailable": True},
    {"code": "IPC", "section_number": "120B", "title": "Criminal conspiracy", "description": "Whoever is a party to a criminal conspiracy to commit an offence punishable with death, imprisonment for life, or rigorous imprisonment for a term of two years or upwards.", "punishment": "Same as for the offence conspired to commit", "bailable": None},
    {"code": "IPC", "section_number": "34", "title": "Acts done by several persons in furtherance of common intention", "description": "When a criminal act is done by several persons in furtherance of the common intention of all, each of such persons is liable for that act as if it were done by him alone.", "punishment": "Same punishment as individual offence", "bailable": None},
    {"code": "IPC", "section_number": "147", "title": "Rioting", "description": "Whoever is guilty of rioting shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.", "punishment": "Imprisonment up to 2 years, or fine, or both", "bailable": False},
    {"code": "IPC", "section_number": "153A", "title": "Promoting enmity between groups", "description": "Whoever promotes or attempts to promote, on grounds of religion, race, place of birth, residence, language, caste or community, disharmony or feelings of enmity between different groups.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": False},
    {"code": "IPC", "section_number": "295A", "title": "Deliberate acts intended to outrage religious feelings", "description": "Deliberate and malicious acts intended to outrage religious feelings of any class by insulting its religion or religious beliefs.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": False},
    {"code": "IPC", "section_number": "411", "title": "Dishonestly receiving stolen property", "description": "Whoever dishonestly receives or retains any stolen property, knowing or having reason to believe the same to be stolen property.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": True},
    {"code": "IPC", "section_number": "193", "title": "Punishment for false evidence", "description": "Whoever intentionally gives false evidence in any stage of a judicial proceeding, or fabricates false evidence for the purpose of being used in any stage of a judicial proceeding.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    # Add more sections for broader coverage
    {"code": "IPC", "section_number": "415", "title": "Cheating", "description": "Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person, or to consent that any person shall retain any property.", "punishment": "Imprisonment up to 1 year, or fine, or both", "bailable": True},
    {"code": "IPC", "section_number": "447", "title": "Criminal trespass", "description": "Whoever commits criminal trespass shall be punished with imprisonment of either description for a term which may extend to three months, or with fine, or with both.", "punishment": "Imprisonment up to 3 months, or fine up to Rs 500, or both", "bailable": True},
    {"code": "IPC", "section_number": "279", "title": "Rash driving or riding on a public way", "description": "Whoever drives any vehicle, or rides, on any public way in a manner so rash or negligent as to endanger human life, or to be likely to cause hurt or injury to any other person.", "punishment": "Imprisonment up to 6 months, or fine up to Rs 1000, or both", "bailable": True},
    {"code": "IPC", "section_number": "304A", "title": "Causing death by negligence", "description": "Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide.", "punishment": "Imprisonment up to 2 years, or fine, or both", "bailable": True},
    {"code": "IPC", "section_number": "509", "title": "Word or gesture intended to insult the modesty of a woman", "description": "Whoever intending to insult the modesty of any woman utters any word, makes any sound or gesture, or exhibits any object, intending that such word or sound shall be heard.", "punishment": "Simple imprisonment up to 3 years, or fine, or both", "bailable": True},
]

# BNS 2023 sections (Bharatiya Nyaya Sanhita — replaces IPC)
_BNS_SECTIONS: list[dict[str, object]] = [
    {"code": "BNS", "section_number": "103", "title": "Murder", "description": "Murder under BNS 2023. Same as IPC 302 but with updated provisions for organised crime and terrorism context.", "punishment": "Death or imprisonment for life and fine", "bailable": False},
    {"code": "BNS", "section_number": "109", "title": "Attempt to murder", "description": "Corresponds to IPC 307. Attempt to commit murder.", "punishment": "Imprisonment up to 10 years, or life if hurt caused", "bailable": False},
    {"code": "BNS", "section_number": "105", "title": "Culpable homicide not amounting to murder", "description": "Corresponds to IPC 304.", "punishment": "Imprisonment for life or up to 10 years", "bailable": False},
    {"code": "BNS", "section_number": "64", "title": "Rape", "description": "Corresponds to IPC 376 with enhanced provisions for repeat offenders and public officials.", "punishment": "Minimum 10 years (from 7 under IPC), may extend to life", "bailable": False},
    {"code": "BNS", "section_number": "303", "title": "Theft", "description": "Corresponds to IPC 379. Theft provisions largely unchanged.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": True},
    {"code": "BNS", "section_number": "305", "title": "Theft in dwelling house", "description": "Corresponds to IPC 380.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "309", "title": "Robbery", "description": "Corresponds to IPC 392.", "punishment": "Rigorous imprisonment up to 10 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "310", "title": "Dacoity", "description": "Corresponds to IPC 395.", "punishment": "Life imprisonment or rigorous imprisonment up to 10 years", "bailable": False},
    {"code": "BNS", "section_number": "318", "title": "Cheating", "description": "Corresponds to IPC 420/415 combined.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "316", "title": "Criminal breach of trust", "description": "Corresponds to IPC 406.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "85", "title": "Cruelty by husband or relatives", "description": "Corresponds to IPC 498A. Expanded to include mental cruelty.", "punishment": "Imprisonment up to 3 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "80", "title": "Dowry death", "description": "Corresponds to IPC 304B.", "punishment": "Minimum 7 years, may extend to life imprisonment", "bailable": False},
    {"code": "BNS", "section_number": "137", "title": "Kidnapping", "description": "Corresponds to IPC 363.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "74", "title": "Assault or criminal force on woman to outrage modesty", "description": "Corresponds to IPC 354 with additions.", "punishment": "Minimum 1 year, may extend to 5 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "115", "title": "Voluntarily causing hurt", "description": "Corresponds to IPC 323.", "punishment": "Imprisonment up to 1 year, or fine, or both", "bailable": True},
    {"code": "BNS", "section_number": "117", "title": "Voluntarily causing grievous hurt", "description": "Corresponds to IPC 325.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "126", "title": "Wrongful restraint", "description": "Corresponds to IPC 341.", "punishment": "Simple imprisonment up to 1 month, or fine", "bailable": True},
    {"code": "BNS", "section_number": "351", "title": "Criminal intimidation", "description": "Corresponds to IPC 506.", "punishment": "Imprisonment up to 2 years, or fine, or both", "bailable": True},
    {"code": "BNS", "section_number": "61", "title": "Criminal conspiracy", "description": "Corresponds to IPC 120B.", "punishment": "Same as for the offence conspired to commit", "bailable": None},
    {"code": "BNS", "section_number": "3(5)", "title": "Acts done in furtherance of common intention", "description": "Corresponds to IPC 34.", "punishment": "Same punishment as individual offence", "bailable": None},
    {"code": "BNS", "section_number": "191", "title": "Rioting", "description": "Corresponds to IPC 147.", "punishment": "Imprisonment up to 2 years, or fine, or both", "bailable": False},
    {"code": "BNS", "section_number": "196", "title": "Promoting enmity between groups", "description": "Corresponds to IPC 153A.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": False},
    {"code": "BNS", "section_number": "302", "title": "Dishonestly receiving stolen property", "description": "Corresponds to IPC 411.", "punishment": "Imprisonment up to 3 years, or fine, or both", "bailable": True},
    {"code": "BNS", "section_number": "229", "title": "Giving false evidence", "description": "Corresponds to IPC 193.", "punishment": "Imprisonment up to 7 years and fine", "bailable": False},
    {"code": "BNS", "section_number": "329", "title": "Criminal trespass", "description": "Corresponds to IPC 447.", "punishment": "Imprisonment up to 3 months, or fine", "bailable": True},
    {"code": "BNS", "section_number": "281", "title": "Rash driving", "description": "Corresponds to IPC 279.", "punishment": "Imprisonment up to 6 months, or fine, or both", "bailable": True},
    {"code": "BNS", "section_number": "106", "title": "Causing death by negligence", "description": "Corresponds to IPC 304A. Enhanced provisions for hit-and-run cases.", "punishment": "Imprisonment up to 5 years and fine (hit-and-run: up to 10 years)", "bailable": True},
    {"code": "BNS", "section_number": "79", "title": "Acts intended to insult modesty of woman", "description": "Corresponds to IPC 509.", "punishment": "Simple imprisonment up to 3 years, or fine, or both", "bailable": True},
]

# IPC to BNS mapping
_IPC_TO_BNS_MAPPINGS: list[dict[str, object]] = [
    {"old_code": "IPC", "old_section": "302", "new_code": "BNS", "new_section": "103", "status": "replaced"},
    {"old_code": "IPC", "old_section": "307", "new_code": "BNS", "new_section": "109", "status": "replaced"},
    {"old_code": "IPC", "old_section": "304", "new_code": "BNS", "new_section": "105", "status": "replaced"},
    {"old_code": "IPC", "old_section": "376", "new_code": "BNS", "new_section": "64", "status": "replaced"},
    {"old_code": "IPC", "old_section": "379", "new_code": "BNS", "new_section": "303", "status": "replaced"},
    {"old_code": "IPC", "old_section": "380", "new_code": "BNS", "new_section": "305", "status": "replaced"},
    {"old_code": "IPC", "old_section": "392", "new_code": "BNS", "new_section": "309", "status": "replaced"},
    {"old_code": "IPC", "old_section": "395", "new_code": "BNS", "new_section": "310", "status": "replaced"},
    {"old_code": "IPC", "old_section": "420", "new_code": "BNS", "new_section": "318", "status": "replaced"},
    {"old_code": "IPC", "old_section": "406", "new_code": "BNS", "new_section": "316", "status": "replaced"},
    {"old_code": "IPC", "old_section": "498A", "new_code": "BNS", "new_section": "85", "status": "replaced"},
    {"old_code": "IPC", "old_section": "304B", "new_code": "BNS", "new_section": "80", "status": "replaced"},
    {"old_code": "IPC", "old_section": "363", "new_code": "BNS", "new_section": "137", "status": "replaced"},
    {"old_code": "IPC", "old_section": "354", "new_code": "BNS", "new_section": "74", "status": "replaced"},
    {"old_code": "IPC", "old_section": "323", "new_code": "BNS", "new_section": "115", "status": "replaced"},
    {"old_code": "IPC", "old_section": "325", "new_code": "BNS", "new_section": "117", "status": "replaced"},
    {"old_code": "IPC", "old_section": "341", "new_code": "BNS", "new_section": "126", "status": "replaced"},
    {"old_code": "IPC", "old_section": "506", "new_code": "BNS", "new_section": "351", "status": "replaced"},
    {"old_code": "IPC", "old_section": "120B", "new_code": "BNS", "new_section": "61", "status": "replaced"},
    {"old_code": "IPC", "old_section": "34", "new_code": "BNS", "new_section": "3(5)", "status": "replaced"},
    {"old_code": "IPC", "old_section": "147", "new_code": "BNS", "new_section": "191", "status": "replaced"},
    {"old_code": "IPC", "old_section": "153A", "new_code": "BNS", "new_section": "196", "status": "replaced"},
    {"old_code": "IPC", "old_section": "411", "new_code": "BNS", "new_section": "302", "status": "replaced"},
    {"old_code": "IPC", "old_section": "193", "new_code": "BNS", "new_section": "229", "status": "replaced"},
    {"old_code": "IPC", "old_section": "447", "new_code": "BNS", "new_section": "329", "status": "replaced"},
    {"old_code": "IPC", "old_section": "304A", "new_code": "BNS", "new_section": "106", "status": "amended"},
    {"old_code": "IPC", "old_section": "509", "new_code": "BNS", "new_section": "79", "status": "replaced"},
]

# Keyword-to-section mapping for case analysis
_KEYWORD_SECTION_MAP: list[tuple[list[str], list[str], str]] = [
    (["murder", "killed", "death", "homicide"], ["IPC-302", "BNS-103"], "murder"),
    (["attempt to murder", "attempted murder"], ["IPC-307", "BNS-109"], "attempt to murder"),
    (["culpable homicide", "manslaughter"], ["IPC-304", "BNS-105"], "culpable homicide"),
    (["rape", "sexual assault"], ["IPC-376", "BNS-64"], "rape"),
    (["theft", "stealing", "stolen"], ["IPC-379", "BNS-303"], "theft"),
    (["dwelling", "house theft", "home theft"], ["IPC-380", "BNS-305"], "dwelling theft"),
    (["robbery", "snatching"], ["IPC-392", "BNS-309"], "robbery"),
    (["dacoity", "gang robbery", "armed robbery"], ["IPC-395", "BNS-310"], "dacoity"),
    (["cheating", "fraud", "deception", "scam"], ["IPC-420", "BNS-318"], "cheating"),
    (["breach of trust", "misappropriation"], ["IPC-406", "BNS-316"], "criminal breach of trust"),
    (["domestic violence", "cruelty by husband", "marital cruelty"], ["IPC-498A", "BNS-85"], "domestic cruelty"),
    (["dowry death", "dowry harassment", "dowry murder"], ["IPC-304B", "BNS-80"], "dowry death"),
    (["kidnapping", "abduction", "missing child"], ["IPC-363", "BNS-137"], "kidnapping"),
    (["molestation", "outrage modesty", "eve teasing physical"], ["IPC-354", "BNS-74"], "assault on modesty"),
    (["hurt", "beating", "assault", "punch", "attack person"], ["IPC-323", "BNS-115"], "causing hurt"),
    (["grievous hurt", "severe injury", "permanent injury"], ["IPC-325", "BNS-117"], "grievous hurt"),
    (["wrongful restraint", "confined", "blocked path"], ["IPC-341", "BNS-126"], "wrongful restraint"),
    (["threat", "intimidation", "threatening"], ["IPC-506", "BNS-351"], "criminal intimidation"),
    (["conspiracy", "planning crime", "gang plan"], ["IPC-120B", "BNS-61"], "criminal conspiracy"),
    (["rioting", "mob violence", "unlawful assembly"], ["IPC-147", "BNS-191"], "rioting"),
    (["communal tension", "religious hatred", "caste violence"], ["IPC-153A", "BNS-196"], "promoting enmity"),
    (["receiving stolen", "buying stolen"], ["IPC-411", "BNS-302"], "receiving stolen property"),
    (["false evidence", "perjury", "false witness"], ["IPC-193", "BNS-229"], "false evidence"),
    (["trespass", "breaking in", "unlawful entry"], ["IPC-447", "BNS-329"], "criminal trespass"),
    (["rash driving", "dangerous driving", "road accident negligence"], ["IPC-279", "BNS-281"], "rash driving"),
    (["negligence death", "accident death", "hit and run"], ["IPC-304A", "BNS-106"], "death by negligence"),
    (["eve teasing", "gesture insult woman", "verbal harassment woman"], ["IPC-509", "BNS-79"], "insulting woman's modesty"),
]


class LegalCodeDatabase:
    """Database of IPC, BNS, CrPC, and BNSS sections with cross-reference lookup."""

    def __init__(self) -> None:
        self._ipc: dict[str, LegalSection] = {
            s["section_number"]: LegalSection(**s)  # type: ignore[arg-type]
            for s in _IPC_SECTIONS
        }
        self._bns: dict[str, LegalSection] = {
            s["section_number"]: LegalSection(**s)  # type: ignore[arg-type]
            for s in _BNS_SECTIONS
        }
        self._mappings: list[LegalMapping] = [
            LegalMapping(**m) for m in _IPC_TO_BNS_MAPPINGS  # type: ignore[arg-type]
        ]
        # Build reverse index: IPC section -> mapping
        self._ipc_to_bns_index: dict[str, LegalMapping] = {
            m.old_section: m for m in self._mappings
        }

    def lookup_ipc(self, section: str) -> LegalSection | None:
        """Look up an IPC section by number."""
        return self._ipc.get(section.strip())

    def lookup_bns(self, section: str) -> LegalSection | None:
        """Look up a BNS section by number."""
        return self._bns.get(section.strip())

    def map_ipc_to_bns(self, ipc_section: str) -> LegalMapping | None:
        """Get the BNS equivalent for an IPC section."""
        return self._ipc_to_bns_index.get(ipc_section.strip())

    def all_ipc(self) -> list[LegalSection]:
        """Return all IPC sections."""
        return list(self._ipc.values())

    def all_bns(self) -> list[LegalSection]:
        """Return all BNS sections."""
        return list(self._bns.values())


class CaseAnalyzer:
    """Analyses case descriptions against Indian law through keyword matching."""

    def __init__(self) -> None:
        self._db = LegalCodeDatabase()

    def analyze(self, case_description: str) -> CaseAnalysis:
        """Perform keyword-based legal analysis on a case description."""
        desc_lower = case_description.lower()
        relevant_sections: list[LegalSection] = []
        ipc_to_bns_mappings: list[dict[str, object]] = []
        matched_categories: list[str] = []
        seen_section_ids: set[str] = set()

        for keywords, section_ids, category in _KEYWORD_SECTION_MAP:
            if any(kw in desc_lower for kw in keywords):
                for sec_id in section_ids:
                    if sec_id in seen_section_ids:
                        continue
                    seen_section_ids.add(sec_id)
                    code, number = sec_id.split("-", 1)
                    if code == "IPC":
                        section = self._db.lookup_ipc(number)
                    elif code == "BNS":
                        section = self._db.lookup_bns(number)
                    else:
                        section = None

                    if section:
                        relevant_sections.append(section)

                if category not in matched_categories:
                    matched_categories.append(category)

                # Add IPC->BNS mapping for matched IPC sections
                for sec_id in section_ids:
                    if sec_id.startswith("IPC-"):
                        ipc_num = sec_id[4:]
                        mapping = self._db.map_ipc_to_bns(ipc_num)
                        if mapping:
                            mapping_dict: dict[str, object] = {
                                "ipc": f"IPC {mapping.old_section}",
                                "bns": f"BNS {mapping.new_section}",
                                "status": mapping.status,
                            }
                            if mapping_dict not in ipc_to_bns_mappings:
                                ipc_to_bns_mappings.append(mapping_dict)

        if not relevant_sections:
            summary = (
                "No specific IPC/BNS sections could be matched to the case description."
                " The case may involve civil law, special statutes, or requires more detail."
                " Consult a qualified advocate for proper legal analysis."
            )
        else:
            ipc_refs = [s.section_number for s in relevant_sections if s.code == "IPC"]
            bns_refs = [s.section_number for s in relevant_sections if s.code == "BNS"]
            summary = (
                f"The case potentially involves the following offences: {', '.join(matched_categories)}. "
            )
            if ipc_refs:
                summary += f"Relevant IPC sections: {', '.join(ipc_refs)}. "
            if bns_refs:
                summary += f"Corresponding BNS 2023 sections: {', '.join(bns_refs)}. "
            summary += (
                "Note: The Bharatiya Nyaya Sanhita (BNS) 2023 replaced the IPC from 1 July 2024."
                " New cases are charged under BNS; old cases under IPC."
            )

        return CaseAnalysis(
            case_description=case_description,
            relevant_sections=relevant_sections,
            ipc_to_bns_mapping=ipc_to_bns_mappings,
            summary=summary,
            disclaimer=LEGAL_DISCLAIMER,
        )
