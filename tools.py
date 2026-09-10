"""
CounselCore Tools Module
=========================
This module contains the custom tools used by the CounselCore agent for legal research.
It provides a local persistent vector database powered by ChromaDB and semantic search,
as well as a template engine for drafting structured legal briefs.

These tools are decorated with Strands Agents SDK's `@tool` decorator, which automatically
parses the function signatures, type hints, and Google-style docstrings to generate
the tool schema for the AI agent.
"""

import os
import sys
import chromadb
from strands import tool

DB_DIR = "./chroma_db"

def get_chroma_client():
    """Retrieves the persistent Chroma DB client, seeding it automatically if missing."""
    if not os.path.exists(DB_DIR):
        print("[*] Local database not found. Running seeder dynamically...")
        try:
            from seed_db import seed_database
            seed_database()
        except Exception as e:
            print(f"[!] Warning: Failed to run database seeder dynamically: {e}")
            
    return chromadb.PersistentClient(path=DB_DIR)


# ==========================================
# 1. Tool Implementations (ChromaDB-Backed)
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
    try:
        client = get_chroma_client()
        collection = client.get_collection(name="case_law")
        
        # Execute semantic search
        results = collection.query(
            query_texts=[query],
            n_results=4
        )
        
        matched_cases = []
        if results and "metadatas" in results and results["metadatas"]:
            metadatas = results["metadatas"][0]
            for meta in metadatas:
                case_jurisdiction = meta.get("jurisdiction", "")
                
                # If jurisdiction filter is provided, enforce a case-insensitive check
                if jurisdiction and jurisdiction.lower() not in case_jurisdiction.lower() and jurisdiction.lower() not in meta.get("name", "").lower():
                    continue
                    
                # Convert comma-separated tags string back into a list of strings
                tags_list = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
                
                matched_cases.append({
                    "name": meta.get("name"),
                    "citation": meta.get("citation"),
                    "court": meta.get("court"),
                    "year": int(meta.get("year", 2024)),
                    "jurisdiction": case_jurisdiction,
                    "facts": meta.get("facts"),
                    "holding": meta.get("holding"),
                    "principle": meta.get("principle"),
                    "tags": tags_list
                })
                
        # If filtering emptied the results, fallback to querying without the jurisdiction filter or return top results
        if not matched_cases and results and "metadatas" in results and results["metadatas"]:
            metadatas = results["metadatas"][0]
            for meta in metadatas[:2]:
                tags_list = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
                matched_cases.append({
                    "name": meta.get("name"),
                    "citation": meta.get("citation"),
                    "court": meta.get("court"),
                    "year": int(meta.get("year", 2024)),
                    "jurisdiction": meta.get("jurisdiction"),
                    "facts": meta.get("facts"),
                    "holding": meta.get("holding"),
                    "principle": meta.get("principle"),
                    "tags": tags_list
                })
                
        return matched_cases

    except Exception as e:
        print(f"[!] Database Search Error: {e}")
        return []


@tool
def lookup_statutes(topic: str) -> list:
    """
    Searches statutory legal frameworks and codes relevant to a given legal topic or issue.

    Args:
        topic: The legal issue, statute name, or section keyword (e.g., 'non-compete', 'CCPA', 'fair use', 'negligence').

    Returns:
        list: A list of relevant statutes with sections, citations, descriptions, and key provisions.
    """
    try:
        client = get_chroma_client()
        collection = client.get_collection(name="statutes")
        
        # Execute semantic search
        results = collection.query(
            query_texts=[topic],
            n_results=3
        )
        
        matched_statutes = []
        if results and "metadatas" in results and results["metadatas"]:
            metadatas = results["metadatas"][0]
            for meta in metadatas:
                # Convert comma-separated tags string back to list
                tags_list = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
                # Convert newline-separated provisions string back to list
                provisions_list = [p.strip() for p in meta.get("provisions", "").split("\n") if p.strip()]
                
                matched_statutes.append({
                    "title": meta.get("title"),
                    "section": meta.get("section"),
                    "jurisdiction": meta.get("jurisdiction"),
                    "description": meta.get("description"),
                    "provisions": provisions_list,
                    "tags": tags_list
                })
                
        return matched_statutes

    except Exception as e:
        print(f"[!] Database Lookup Error: {e}")
        return []


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
