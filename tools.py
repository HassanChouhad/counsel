"""
CounselCore Tools Module
=========================
This module contains the custom tools used by the CounselCore agent for legal research.
It provides mocked databases and dynamic keyword matching for case law and statutes,
as well as a template engine for drafting structured legal briefs.

These tools are decorated with Strands Agents SDK's `@tool` decorator, which automatically
parses the function signatures, type hints, and Google-style docstrings to generate
the tool schema for the AI agent.
"""

from strands import tool

# ==========================================
# 1. Mock Legal Database (Realistic Precedents)
# ==========================================
MOCK_CASES = [
    {
        "name": "NovaTech Solutions v. Apex Systems Corp.",
        "citation": "842 F.3d 1105 (9th Cir. 2023)",
        "court": "United States Court of Appeals for the Ninth Circuit",
        "year": 2023,
        "jurisdiction": "California / Federal / 9th Circuit",
        "facts": "An employer sought to enforce a nationwide non-compete clause against a former software architect. The agreement barred employment with any tech company for three years.",
        "holding": "The non-compete clause was found to be overly broad and geographically unreasonable, making it completely unenforceable under California Business and Professions Code Section 16600.",
        "principle": "Restrictive covenants in employment agreements must have a reasonable geographical scope, a limited duration, and protect a clear legitimate interest (such as trade secrets). In California, non-compete agreements are void ab initio except in extremely narrow statutory exceptions.",
        "tags": ["non-compete", "restrictive covenant", "employment", "contract", "california", "geographic scope"]
    },
    {
        "name": "Summit Logistics Group v. Miller",
        "citation": "512 S.W.3d 88 (Tex. App. 2021)",
        "court": "Texas Court of Appeals",
        "year": 2021,
        "jurisdiction": "Texas State Court",
        "facts": "A logistics company sued a former sales executive for breaching a 1-year, 50-mile radius non-compete covenant and soliciting former clients using proprietary customer lists.",
        "holding": "The court upheld the non-compete as reasonable in duration and geographic scope, and found the customer lists constituted protectable trade secrets under the Texas Uniform Trade Secrets Act (TUTSA).",
        "principle": "Covenants not to compete are enforceable in Texas if they are ancillary to or part of an otherwise enforceable agreement, and contain reasonable limitations as to time, geographical area, and scope of activity.",
        "tags": ["non-compete", "employment", "contract", "texas", "trade secrets", "solicitation", "restrictive covenant"]
    },
    {
        "name": "Creative Designs Inc. v. PixelCraft LLC",
        "citation": "921 F. Supp. 2d 441 (S.D.N.Y. 2022)",
        "court": "U.S. District Court for the Southern District of New York",
        "year": 2022,
        "jurisdiction": "New York / Federal / S.D.N.Y.",
        "facts": "Plaintiff sued PixelCraft for copyright infringement, claiming PixelCraft's AI-generated marketing materials copied original vector graphics owned by Plaintiff. PixelCraft claimed fair use.",
        "holding": "The court rejected the fair use defense, finding that PixelCraft's commercial application directly competed with the original market and copied the expressive essence of the graphics without transformative purpose.",
        "principle": "Fair use analysis requires balancing four statutory factors: purpose of use, nature of copyrighted work, amount/substantiality of portion used, and effect on the market. Commercial, non-transformative copying that damages the original market is rarely considered fair use.",
        "tags": ["copyright", "fair use", "infringement", "intellectual property", "digital assets", "new york", "commercial", "patent", "trademark"]
    },
    {
        "name": "Dr. Angela Carter v. St. Jude Medical Center",
        "citation": "310 Mass. 182 (2020)",
        "court": "Supreme Judicial Court of Massachusetts",
        "year": 2020,
        "jurisdiction": "Massachusetts State Court",
        "facts": "A patient suffered severe complications following a surgical procedure where the surgeon deviated from standard pre-operative checklist protocols, leading to an undetected internal infection.",
        "holding": "The court affirmed a jury verdict for the plaintiff, holding that deviation from standard hospital protocol can be introduced as direct evidence of a breach of the professional standard of care.",
        "principle": "Medical malpractice requires establishing: (1) a physician-patient relationship creating a duty of care, (2) deviation from the accepted professional standard of care, (3) a causal link between deviation and injury (proximate cause), and (4) quantifiable damages.",
        "tags": ["negligence", "medical malpractice", "standard of care", "personal injury", "massachusetts", "causation", "liability", "injury"]
    },
    {
        "name": "In re Sentinel Data Solutions Privacy Litigation",
        "citation": "452 F. Supp. 3d 910 (N.D. Cal. 2024)",
        "court": "U.S. District Court for the Northern District of California",
        "year": 2024,
        "jurisdiction": "California / Federal / N.D. Cal.",
        "facts": "A class-action suit was filed against a cloud service provider after a misconfigured database exposed personal health information (PHI) and financial records of over 2 million consumers.",
        "holding": "The court denied the defendant's motion to dismiss, ruling that failure to implement basic security controls (like encryption at rest and access logs) constituted a plausible claim for negligence and violated statutory consumer privacy duties.",
        "principle": "Under modern data protection frameworks, companies owe a duty of reasonable care to secure sensitive personal data. Showing failure to apply standard industry frameworks (e.g., NIST, CIS) can establish a breach of that duty.",
        "tags": ["privacy", "data breach", "negligence", "california", "cybersecurity", "duty of care", "leak", "security"]
    }
]

# ==========================================
# 2. Mock Legal Database (Realistic Statutes)
# ==========================================
MOCK_STATUTES = [
    {
        "title": "California Business and Professions Code - Void Contracts",
        "section": "Cal. Bus. & Prof. Code § 16600",
        "jurisdiction": "California, USA",
        "description": "Except as provided in this chapter, every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void.",
        "provisions": [
            "Voiding of restrictive covenants: Declares non-compete agreements in employment context strictly invalid.",
            "Exceptions: Limited to sale of business goodwill, partnership dissolution, or LLC member dissociation."
        ],
        "tags": ["non-compete", "employment", "contract", "california", "restrictive covenant"]
    },
    {
        "title": "Texas Covenants Not to Compete Act",
        "section": "Tex. Bus. & Com. Code § 15.50",
        "jurisdiction": "Texas, USA",
        "description": "Governs the enforceability of covenants not to compete in the state of Texas.",
        "provisions": [
            "Enforceability: Must be ancillary to or part of an otherwise enforceable agreement.",
            "Reasonableness: Must contain reasonable limitations as to time, geographical area, and scope of activity to be restrained.",
            "Remedies: Courts may reform an overbroad covenant to make it reasonable, though damages are restricted prior to reformation."
        ],
        "tags": ["non-compete", "employment", "contract", "texas", "restrictive covenant"]
    },
    {
        "title": "The Copyright Act of 1976 - Fair Use Doctrine",
        "section": "17 U.S.C. § 107",
        "jurisdiction": "Federal (United States)",
        "description": "Establishes the limitations on exclusive rights, specifically the fair use of a copyrighted work.",
        "provisions": [
            "Purpose of use: Character of use, including commercial or non-profit educational purposes.",
            "Nature of work: Degree of creativity and publication status.",
            "Amount used: Substantiality of the portion used in relation to the copyrighted work as a whole.",
            "Market impact: The effect of the use upon the potential market for or value of the copyrighted work."
        ],
        "tags": ["copyright", "fair use", "infringement", "intellectual property", "patent", "trademark"]
    },
    {
        "title": "California Consumer Privacy Act (CCPA) / CPRA",
        "section": "Cal. Civ. Code § 1798.100 et seq.",
        "jurisdiction": "California, USA",
        "description": "Comprehensive state statute protecting consumer privacy rights and establishing security obligations.",
        "provisions": [
            "Duty of Security: Businesses must maintain reasonable security procedures and practices.",
            "Private Right of Action: Allows consumers to sue for statutory damages ($100-$750 per consumer per incident) in the event of unauthorized access, exfiltration, or disclosure resulting from failure to maintain reasonable security."
        ],
        "tags": ["privacy", "data breach", "california", "cybersecurity", "security", "leak"]
    },
    {
        "title": "Restatement (Second) of Torts - Elements of Negligence",
        "section": "Restatement (Second) of Torts § 281 et seq.",
        "jurisdiction": "Common Law / Multi-state",
        "description": "Defines the essential elements of a cause of action for negligence under US common law.",
        "provisions": [
            "Elements of Negligence: A plaintiff must establish: (a) a legal duty of care, (b) a breach of that duty, (c) a causal connection (proximate cause), and (d) actual loss or damage.",
            "Standard of Care: The standard is that of a reasonable person under like circumstances, or a specialized professional standard for doctors, lawyers, or engineers."
        ],
        "tags": ["negligence", "medical malpractice", "duty of care", "liability", "damages", "injury"]
    }
]


# ==========================================
# 3. Tool Implementations (Decorated)
# ==========================================

@tool
def search_case_law(query: str, jurisdiction: str = "") -> list:
    """
    Searches a curated repository of precedent case law based on facts, keywords, or jurisdiction.

    Args:
        query: Keywords, case facts, or legal topics to search for (e.g., 'non-compete', 'copyright', 'medical malpractice').
        jurisdiction: Optional geographic or court filter (e.g., 'California', 'Texas', 'Federal').

    Returns:
        list: A list of matching precedent cases, containing names, citations, holdings, and principles.
    """
    query_lower = query.lower()
    j_lower = jurisdiction.lower() if jurisdiction else ""
    
    results = []
    for case in MOCK_CASES:
        score = 0
        
        # 1. Jurisdiction Match
        if j_lower and (j_lower in case["jurisdiction"].lower() or j_lower in case["name"].lower()):
            score += 5
            
        # 2. Tag Match
        for tag in case["tags"]:
            if tag in query_lower:
                score += 3
                
        # 3. Text/Facts/Holding Match
        if any(word in case["facts"].lower() for word in query_lower.split() if len(word) > 4):
            score += 1
        if any(word in case["principle"].lower() for word in query_lower.split() if len(word) > 4):
            score += 1
        if any(word in case["name"].lower() for word in query_lower.split() if len(word) > 4):
            score += 1
            
        if score > 0:
            results.append((score, case))
            
    # Sort by relevance score descending
    results.sort(key=lambda x: x[0], reverse=True)
    matched_cases = [item[1] for item in results]
    
    # If no results matched, return a default safe selection of general precedents to keep the agent operational
    if not matched_cases:
        # Fallback to returning cases based on a simple keyword presence or just return top 2
        return MOCK_CASES[:2]
        
    return matched_cases


@tool
def lookup_statutes(topic: str) -> list:
    """
    Searches statutory legal frameworks and codes relevant to a given legal topic or issue.

    Args:
        topic: The legal issue, statute name, or section keyword (e.g., 'non-compete', 'CCPA', 'fair use', 'negligence').

    Returns:
        list: A list of relevant statutes with sections, citations, descriptions, and key provisions.
    """
    topic_lower = topic.lower()
    
    results = []
    for statute in MOCK_STATUTES:
        score = 0
        
        # 1. Tag Match
        for tag in statute["tags"]:
            if tag in topic_lower:
                score += 3
                
        # 2. Text/Description Match
        if any(word in statute["description"].lower() for word in topic_lower.split() if len(word) > 4):
            score += 1
        if any(word in statute["title"].lower() for word in topic_lower.split() if len(word) > 4):
            score += 1
            
        if score > 0:
            results.append((score, statute))
            
    # Sort by relevance score descending
    results.sort(key=lambda x: x[0], reverse=True)
    matched_statutes = [item[1] for item in results]
    
    # Fallback to returning top 2 general statutes if nothing matches
    if not matched_statutes:
        return MOCK_STATUTES[:2]
        
    return matched_statutes


@tool
def draft_legal_brief(case_facts: str, precedents: list, statutes: list) -> str:
    """
    Synthesizes facts, precedent cases, and statutory codes into a structured, highly professional markdown legal brief.

    Args:
        case_facts: The raw background information, user inputs, and circumstances of the case.
        precedents: A list of dictionaries representing case law findings from search_case_law.
        statutes: A list of dictionaries representing statutory findings from lookup_statutes.

    Returns:
        str: A fully formatted markdown legal strategy document.
    """
    
    # Format Statutes Section
    statutes_section = ""
    if statutes:
        for idx, stat in enumerate(statutes, 1):
            provisions_list = "\n".join([f"    * {p}" for p in stat.get('provisions', [])])
            statutes_section += f"""
### {idx}. {stat.get('title')}
* **Citation:** `{stat.get('section')}`
* **Jurisdiction:** {stat.get('jurisdiction')}
* **Overview:** {stat.get('description')}
* **Key Provisions:**
{provisions_list}
"""
    else:
        statutes_section = "\n*No specific statutory sections were referenced. Common law rules apply.*\n"

    # Format Precedents Section
    precedents_section = ""
    if precedents:
        for idx, case in enumerate(precedents, 1):
            precedents_section += f"""
### {idx}. {case.get('name')}
* **Citation:** *{case.get('citation')}* ({case.get('court')}, {case.get('year')})
* **Jurisdiction:** {case.get('jurisdiction')}
* **Factual Matrix:** {case.get('facts')}
* **Holding:** {case.get('holding')}
* **Core Legal Principle:** {case.get('principle')}
"""
    else:
        precedents_section = "\n*No binding judicial precedents were referenced.*\n"

    # Determine general area of law to customize the analysis slightly
    area_of_law = "General Civil Matter"
    facts_lower = case_facts.lower()
    if "non-compete" in facts_lower or "employment" in facts_lower or "contract" in facts_lower:
        area_of_law = "Employment Law / Restrictive Covenants"
    elif "copyright" in facts_lower or "fair use" in facts_lower or "patent" in facts_lower or "trademark" in facts_lower:
        area_of_law = "Intellectual Property Litigation"
    elif "medical" in facts_lower or "negligence" in facts_lower or "injury" in facts_lower or "malpractice" in facts_lower:
        area_of_law = "Tort Liability / Professional Negligence"
    elif "privacy" in facts_lower or "data breach" in facts_lower or "security" in facts_lower:
        area_of_law = "Cybersecurity & Data Privacy Law"

    # Assemble complete legal brief in structured markdown
    brief = f"""# COUNSELCORE: PRELIMINARY LEGAL STRATEGY BRIEF
**CONFIDENTIAL // ATTORNEY-CLIENT PRIVILEGE**

---

## 1. EXECUTIVE SUMMARY & ENGAGEMENT METRICS
* **Matter Category:** {area_of_law}
* **Generated By:** CounselCore Autonomous Legal Research Agent
* **Platform:** AWS Bedrock (Claude Engine) & Strands Agents SDK
* **Status:** Draft (For Internal Attorney Review Only)

### Brief Summary
This strategy document has been autonomously compiled by parsing client case notes, querying our curated legal databases for statutory framework and judicial precedents, and synthesizing the findings. The primary objective is to evaluate potential liabilities, outline defenses, and formulate a step-by-step litigation or compliance strategy.

---

## 2. STATEMENT OF CLIENT FACTS
Below is the factual background provided for evaluation:

> {case_facts.strip()}

---

## 3. STATUTORY FRAMEWORK & LEGISLATIVE AUTHORITY
The following statutory sections have been identified as highly relevant to this matter:
{statutes_section}

---

## 4. JUDICIAL PRECEDENTS & CASE LAW ANALYSIS
The following binding or persuasive judicial precedents provide guidance on how courts interpret these issues:
{precedents_section}

---

## 5. STRATEGIC ANALYSIS & LEGAL ASSESSMENT

### Strengths of the Client's Position
* **Statutory Compliance / Protections:** If applicable, state statutes provide strong consumer or employee protections which may invalidate the opposition's claims or strengthen the client's cause of action.
* **Precedential Support:** Key holdings in precedent cases align closely with the core facts here (e.g., requirements of reasonableness, standard of care, or fair use criteria).
* **Factual Merits:** The client's actions demonstrate a reasonable, good-faith attempt to comply with standard procedures or laws.

### Weaknesses & Potential Vulnerabilities
* **Geographical and Jurisdictional Ambiguities:** Differences in state-level enforcement (e.g., California vs. Texas on non-competes) create significant venue risks.
* **Factual Distinctions:** The opposition may attempt to distinguish precedent cases by highlighting differences in commercial impact or professional relationships.
* **Evidentiary Gaps:** Success may heavily depend on establishing specific proof, such as demonstrating exact "transformative use," proving standard of care deviations, or documenting reasonable security measures.

---

## 6. RECOMMENDED ACTION PLAN & NEXT STEPS
1. **Jurisdictional Selection (Venue):** Carefully choose the filing venue or respond in a venue that maximizes favorable law (e.g., seeking California jurisdiction for non-compete matters).
2. **Document Preservation & Discovery:** Issue immediate litigation hold letters and preserve all relevant communications, contracts, protocols, or logs.
3. **Drafting Pleadings:** Utilize the statutory and precedential arguments outlined in Sections 3 and 4 as the foundation for the Answer, Motion to Dismiss, or Complaint.
4. **Expert Witness Engagement:** In professional negligence or data breach cases, identify potential expert witnesses to establish standard of care or industry standards.

---
*Disclaimer: CounselCore is an AI legal research agent powered by AWS Bedrock and the Strands Agents SDK. This document is a preliminary work product intended to assist licensed legal professionals. It does not constitute formal, binding legal advice.*
"""
    return brief
