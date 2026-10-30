import re
from collections import defaultdict
from datetime import datetime

from pypdf import PdfReader

from skill_extractor import extract_skills_with_evidence, skill_category


_SECTION_LABELS = {
    "summary": "summary",
    "profile": "summary",
    "objective": "summary",
    "career objective": "summary",
    "technical skills": "skills",
    "core competencies": "skills",
    "skills": "skills",
    "soft skills": "soft_skills",
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "career history": "experience",
    "employment history": "experience",
    "work history": "experience",
    "professional background": "experience",
    "internship": "internships",
    "internships": "internships",
    "internship experience": "internships",
    "projects": "projects",
    "key projects": "projects",
    "selected projects": "projects",
    "selected work": "projects",
    "academic projects": "projects",
    "relevant projects": "projects",
    "project experience": "projects",
    "personal projects": "projects",
    "education": "education",
    "academic background": "education",
    "certifications": "certifications",
    "certification": "certifications",
    "certificates": "certifications",
    "licenses": "certifications",
}

_SECTION_PATTERN = "|".join(
    re.escape(label)
    for label in sorted(_SECTION_LABELS, key=len, reverse=True)
)
_HEADING_RE = re.compile(
    rf"^\s*({_SECTION_PATTERN})(?:\s*[:\-]\s*(.*))?\s*$",
    re.I,
)
_DEGREE_RE = re.compile(
    r"\b(?:"
    r"Ph\.?\s?D\.?|doctorate|"
    r"master(?:'s)?(?:\s+degree)?|M\.?\s?(?:Tech|Sc|S|C|BA|A)\.?|"
    r"bachelor(?:'s)?(?:\s+degree)?|B\.?\s?(?:Tech|Sc|S|C|BA|A)\.?|"
    r"diploma|associate(?:'s)?(?:\s+degree)?|"
    r"higher secondary|high school"
    r")\b",
    re.I,
)
_YEARS_EXPERIENCE_RE = re.compile(
    r"\b(?P<years>\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"
    r"(?:\s+of\s+(?:professional\s+|relevant\s+)?experience"
    r"|\s+(?:professional\s+|business\s+)?experience"
    r"|\s+as\b)",
    re.I,
)
_DATE_RANGE_RE = re.compile(
    r"\b(?P<start>(?:19|20)\d{2})\s*[-–—]\s*"
    r"(?P<end>(?:(?:19|20)\d{2})|present|current|now)\b",
    re.I,
)
_ROLE_DATE_RE = re.compile(
    r"(?P<role>[A-Z][A-Za-z0-9/&+., -]{1,70}?),\s*"
    r"[^;:()]{1,70}\((?:19|20)\d{2}\s*[-–—]\s*"
    r"(?:(?:19|20)\d{2}|Present|Current|Now)\)",
    re.I,
)
_ROLE_AT_RE = re.compile(
    r"^(?P<role>[A-Z][A-Za-z0-9/&+., -]{1,70}?)\s+(?:at|@)\s+"
    r"[A-Z][A-Za-z0-9&., -]{1,70}$"
)


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _split_resume_sections(text):
    cleaned = text.replace("\r", "\n")
    cleaned = re.sub(r"[•▪●]", "\n", cleaned)
    cleaned = re.sub(
        rf"\s+(?=(?:{_SECTION_PATTERN})\s*[:\-])",
        "\n",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"\s*\|\|?\s*", "\n", cleaned)

    sections = defaultdict(list)
    current_section = "other"
    for raw_line in cleaned.splitlines():
        line = raw_line.strip(" \t-–")
        if not line:
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            current_section = _SECTION_LABELS[heading.group(1).casefold()]
            body = (heading.group(2) or "").strip()
            if body:
                sections[current_section].append(body)
            continue
        sections[current_section].append(line)

    return {name: entries for name, entries in sections.items()}


def _entries(section_text):
    entries = []
    for block in section_text:
        entries.extend(
            item.strip(" \t-–•")
            for item in re.split(r"\s*(?:\|\||\n|•|▪|●)\s*", block)
            if item.strip(" \t-–•")
        )
    return entries


def _experience_years(text, experience_sections, internship_sections):
    reported_years = [
        float(match.group("years"))
        for match in _YEARS_EXPERIENCE_RE.finditer(text)
    ]

    current_year = datetime.now().year

    def dated_years(sections):
        ranges = []
        for section in sections:
            for match in _DATE_RANGE_RE.finditer(section):
                start = int(match.group("start"))
                end_text = match.group("end")
                end = current_year if end_text.casefold() in {
                    "present", "current", "now"
                } else int(end_text)
                if start <= end <= current_year + 1:
                    ranges.append((start, end))
        if not ranges:
            return 0.0
        ranges.sort()
        merged = []
        for start, end in ranges:
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        return float(sum(end - start for start, end in merged))

    work_years = dated_years(experience_sections)
    internship_years = dated_years(internship_sections)
    inferred_total = work_years + internship_years * 0.5
    available = reported_years + ([inferred_total] if inferred_total else [])
    return (round(max(available), 1) if available else None), work_years, internship_years


def _records(entries, section_name):
    records = []
    for evidence in entries:
        if section_name == "education":
            degree_match = _DEGREE_RE.search(evidence)
            records.append({
                "degree": degree_match.group(0) if degree_match else None,
                "evidence": evidence,
            })
        elif section_name == "projects":
            name = re.split(r"\s+[-–:]\s+", evidence, maxsplit=1)[0].strip()
            records.append({"name": name or None, "evidence": evidence})
        elif section_name == "certifications":
            records.append({"name": evidence, "evidence": evidence})
        else:
            role_match = _ROLE_DATE_RE.search(evidence) or _ROLE_AT_RE.match(
                evidence
            )
            records.append({
                "role": role_match.group("role").strip() if role_match else None,
                "evidence": evidence,
            })
    return records


def build_candidate_profile(text):
    if not isinstance(text, str) or not text.strip():
        return {
            "candidate_level": "unknown",
            "experience_years": None,
            "education": [],
            "work_experience": [],
            "internships": [],
            "technical_skills": [],
            "soft_skills": [],
            "certifications": [],
            "projects": [],
            "data_quality_warnings": ["No readable resume text was provided."],
        }

    sections = _split_resume_sections(text)
    experience_sections = sections.get("experience", [])
    internship_sections = sections.get("internships", [])
    experience_years, work_years, internship_years = _experience_years(
        text, experience_sections, internship_sections
    )

    education = _records(_entries(sections.get("education", [])), "education")
    work_experience = _records(_entries(experience_sections), "experience")
    internships = _records(_entries(internship_sections), "internships")
    projects = _records(_entries(sections.get("projects", [])), "projects")
    certifications = _records(
        _entries(sections.get("certifications", [])), "certifications"
    )

    skill_sections = list(sections.items())
    if not any(entries for _, entries in skill_sections):
        skill_sections.append(("other", [text]))

    skills_by_name = {}
    for section_name, entries in skill_sections:
        for evidence_text in entries:
            for found in extract_skills_with_evidence(evidence_text):
                item = skills_by_name.setdefault(
                    found["skill"],
                    {
                        "skill": found["skill"],
                        "category": skill_category(found["skill"]),
                        "evidence": [],
                    },
                )
                evidence = {
                    "section": section_name,
                    "text": found["evidence"],
                }
                if evidence not in item["evidence"]:
                    item["evidence"].append(evidence)

    skills = sorted(skills_by_name.values(), key=lambda item: item["skill"].casefold())
    technical_skills = [item for item in skills if item["category"] == "technical"]
    soft_skills = [item for item in skills if item["category"] == "soft"]

    has_student_evidence = bool(
        re.search(r"\b(?:student|fresher|recent graduate|new graduate)\b", text, re.I)
    ) or bool(education)
    role_evidence = " ".join(
        [
            *sections.get("summary", []),
            *(
                record.get("role") or record.get("evidence", "")
                for record in work_experience
            ),
        ]
    )
    if experience_years is not None and experience_years >= 3:
        candidate_level = "experienced"
    elif experience_years is not None and experience_years >= 1:
        candidate_level = "junior"
    elif internships and not work_experience and (
        experience_years is None or experience_years < 1
    ):
        candidate_level = "intern"
    elif work_experience:
        if re.search(r"\b(?:senior|lead|principal|staff|experienced)\b", role_evidence, re.I):
            candidate_level = "experienced"
        elif re.search(r"\b(?:junior|associate|trainee|entry.level)\b", role_evidence, re.I):
            candidate_level = "junior"
        else:
            candidate_level = "unknown"
    elif internships:
        candidate_level = "intern"
    elif has_student_evidence or projects:
        candidate_level = "fresher"
    else:
        candidate_level = "unknown"

    warnings = []
    if not technical_skills:
        warnings.append("No technical skills could be verified from the resume text.")
    if not any(item["degree"] for item in education):
        warnings.append("No explicit degree evidence was found.")
    if not work_experience and not internships:
        warnings.append("No work experience or internship evidence was found.")
    if experience_years is None:
        warnings.append("Years of experience could not be determined from explicit evidence.")
    if not projects:
        warnings.append("No project evidence was found.")
    if len(text.strip()) < 120:
        warnings.append("The resume text is short; profile and match confidence may be limited.")

    return {
        "candidate_level": candidate_level,
        "experience_years": experience_years,
        "work_experience_years": round(work_years, 1),
        "internship_years": round(internship_years, 1),
        "education": education,
        "work_experience": work_experience,
        "internships": internships,
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "certifications": certifications,
        "projects": projects,
        "data_quality_warnings": warnings,
    }
