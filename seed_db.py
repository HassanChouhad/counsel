#!/usr/bin/env python3
"""
seed_db.py
================================================================================
A database seeder script for CounselCore that populates a local persistent
ChromaDB instance with landmark case laws and statutory codes.
This establishes the RAG (Retrieval-Augmented Generation) foundation.
================================================================================
"""

import os
import shutil
import chromadb
from chromadb.utils import embedding_functions

# Define database directory
DB_DIR = "./chroma_db"

# Sample Legal Data
CASES = [
    {
        "id": "case_novatech_2023",
        "name": "NovaTech Solutions v. Apex Systems Corp.",
        "citation": "842 F.3d 1105 (9th Cir. 2023)",
        "court": "United States Court of Appeals for the Ninth Circuit",
        "year": 2023,
        "jurisdiction": "California / Federal / 9th Circuit",
        "facts": "An employer sought to enforce a nationwide non-compete clause against a former software architect. The agreement barred employment with any tech company for three years.",
        "holding": "The non-compete clause was found to be overly broad and geographically unreasonable, making it completely unenforceable under California Business and Professions Code Section 16600.",
        "principle": "Restrictive covenants in employment agreements must have a reasonable geographical scope, a limited duration, and protect a clear legitimate interest (such as trade secrets). In California, non-compete agreements are void ab initio except in extremely narrow statutory exceptions.",
        "tags": "non-compete, restrictive covenant, employment, contract, california, geographic scope"
    },
    {
        "id": "case_summit_2021",
        "name": "Summit Logistics Group v. Miller",
        "citation": "512 S.W.3d 88 (Tex. App. 2021)",
        "court": "Texas Court of Appeals",
        "year": 2021,
        "jurisdiction": "Texas State Court",
        "facts": "A logistics company sued a former sales executive for breaching a 1-year, 50-mile radius non-compete covenant and soliciting former clients using proprietary customer lists.",
        "holding": "The court upheld the non-compete as reasonable in duration and geographic scope, and found the customer lists constituted protectable trade secrets under the Texas Uniform Trade Secrets Act (TUTSA).",
        "principle": "Covenants not to compete are enforceable in Texas if they are ancillary to or part of an otherwise enforceable agreement, and contain reasonable limitations as to time, geographical area, and scope of activity.",
        "tags": "non-compete, employment, contract, texas, trade secrets, solicitation, restrictive covenant"
    },
    {
        "id": "case_pixelcraft_2022",
        "name": "Creative Designs Inc. v. PixelCraft LLC",
        "citation": "921 F. Supp. 2d 441 (S.D.N.Y. 2022)",
        "court": "U.S. District Court for the Southern District of New York",
        "year": 2022,
        "jurisdiction": "New York / Federal / S.D.N.Y.",
        "facts": "Plaintiff sued PixelCraft for copyright infringement, claiming PixelCraft's AI-generated marketing materials copied original vector graphics owned by Plaintiff. PixelCraft claimed fair use.",
        "holding": "The court rejected the fair use defense, finding that PixelCraft's commercial application directly competed with the original market and copied the expressive essence of the graphics without transformative purpose.",
        "principle": "Fair use analysis requires balancing four statutory factors: purpose of use, nature of copyrighted work, amount/substantiality of portion used, and effect on the market. Commercial, non-transformative copying that damages the original market is rarely considered fair use.",
        "tags": "copyright, fair use, infringement, intellectual property, digital assets, new york, commercial, patent, trademark"
    },
    {
        "id": "case_carter_2020",
        "name": "Dr. Angela Carter v. St. Jude Medical Center",
        "citation": "310 Mass. 182 (2020)",
        "court": "Supreme Judicial Court of Massachusetts",
        "year": 2020,
        "jurisdiction": "Massachusetts State Court",
        "facts": "A patient suffered severe complications following a surgical procedure where the surgeon deviated from standard pre-operative checklist protocols, leading to an undetected internal infection.",
        "holding": "The court affirmed a jury verdict for the plaintiff, holding that deviation from standard hospital protocol can be introduced as direct evidence of a breach of the professional standard of care.",
        "principle": "Medical malpractice requires establishing: (1) a physician-patient relationship creating a duty of care, (2) deviation from the accepted professional standard of care, (3) a causal link between deviation and injury (proximate cause), and (4) quantifiable damages.",
        "tags": "negligence, medical malpractice, standard of care, personal injury, massachusetts, causation, liability, injury"
    },
    {
        "id": "case_sentinel_2024",
        "name": "In re Sentinel Data Solutions Privacy Litigation",
        "citation": "452 F. Supp. 3d 910 (N.D. Cal. 2024)",
        "court": "U.S. District Court for the Northern District of California",
        "year": 2024,
        "jurisdiction": "California / Federal / N.D. Cal.",
        "facts": "A class-action suit was filed against a cloud service provider after a misconfigured database exposed personal health information (PHI) and financial records of over 2 million consumers.",
        "holding": "The court denied the defendant's motion to dismiss, ruling that failure to implement basic security controls (like encryption at rest and access logs) constituted a plausible claim for negligence and violated statutory consumer privacy duties.",
        "principle": "Under modern data protection frameworks, companies owe a duty of reasonable care to secure sensitive personal data. Showing failure to apply standard industry frameworks (e.g., NIST, CIS) can establish a breach of that duty.",
        "tags": "privacy, data breach, negligence, california, cybersecurity, duty of care, leak, security"
    },
    {
        "id": "case_campbell_1994",
        "name": "Campbell v. Acuff-Rose Music, Inc.",
        "citation": "510 U.S. 569 (1994)",
        "court": "Supreme Court of the United States",
        "year": 1994,
        "jurisdiction": "Federal / US Supreme Court",
        "facts": "The rap group 2 Live Crew released a commercial parody of Roy Orbison's song 'Oh, Pretty Woman'. Acuff-Rose Music sued for copyright infringement. 2 Live Crew claimed fair use.",
        "holding": "The Supreme Court held that parody can be fair use under 17 U.S.C. § 107. The commercial nature of a work does not automatically bar a finding of fair use, especially when the parody is transformative.",
        "principle": "The more transformative the new work, the less will be the significance of other factors, like commercialism, that may weigh against a finding of fair use.",
        "tags": "copyright, fair use, parody, music, transformative use, intellectual property"
    },
    {
        "id": "case_tarasoff_1976",
        "name": "Tarasoff v. Regents of the University of California",
        "citation": "17 Cal.3d 425 (1976)",
        "court": "Supreme Court of California",
        "year": 1976,
        "jurisdiction": "California State Court",
        "facts": "A patient told his university therapist he intended to kill a specific named student. The therapist notified campus police but failed to warn the victim or her parents. The patient subsequently killed the student.",
        "holding": "The court held that mental health professionals have a duty to protect individuals who are being specifically threatened with bodily harm by a patient.",
        "principle": "The protective privilege of confidentiality ends where the public peril begins. When a therapist determines that a patient poses a serious danger of violence to another, they incur an obligation to use reasonable care to protect the intended victim.",
        "tags": "negligence, duty of care, duty to warn, therapist, psychiatric, personal injury, california"
    }
]

STATUTES = [
    {
        "id": "stat_cal_16600",
        "title": "California Business and Professions Code - Void Contracts",
        "section": "Cal. Bus. & Prof. Code § 16600",
        "jurisdiction": "California, USA",
        "description": "Except as provided in this chapter, every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void.",
        "provisions": "1. Voiding of restrictive covenants: Declares non-compete agreements in employment context strictly invalid.\n2. Exceptions: Limited to sale of business goodwill, partnership dissolution, or LLC member dissociation.",
        "tags": "non-compete, employment, contract, california, restrictive covenant"
    },
    {
        "id": "stat_tex_15_50",
        "title": "Texas Covenants Not to Compete Act",
        "section": "Tex. Bus. & Com. Code § 15.50",
        "jurisdiction": "Texas, USA",
        "description": "Governs the enforceability of covenants not to compete in the state of Texas.",
        "provisions": "1. Enforceability: Must be ancillary to or part of an otherwise enforceable agreement.\n2. Reasonableness: Must contain reasonable limitations as to time, geographical area, and scope of activity to be restrained.\n3. Remedies: Courts may reform an overbroad covenant to make it reasonable, though damages are restricted prior to reformation.",
        "tags": "non-compete, employment, contract, texas, restrictive covenant"
    },
    {
        "id": "stat_us_107",
        "title": "The Copyright Act of 1976 - Fair Use Doctrine",
        "section": "17 U.S.C. § 107",
        "jurisdiction": "Federal (United States)",
        "description": "Establishes the limitations on exclusive rights, specifically the fair use of a copyrighted work.",
        "provisions": "1. Purpose of use: Character of use, including commercial or non-profit educational purposes.\n2. Nature of work: Degree of creativity and publication status.\n3. Amount used: Substantiality of the portion used in relation to the copyrighted work as a whole.\n4. Market impact: The effect of the use upon the potential market for or value of the copyrighted work.",
        "tags": "copyright, fair use, infringement, intellectual property, patent, trademark"
    },
    {
        "id": "stat_cal_ccpa",
        "title": "California Consumer Privacy Act (CCPA) / CPRA",
        "section": "Cal. Civ. Code § 1798.100 et seq.",
        "jurisdiction": "California, USA",
        "description": "Comprehensive state statute protecting consumer privacy rights and establishing security obligations.",
        "provisions": "1. Duty of Security: Businesses must maintain reasonable security procedures and practices.\n2. Private Right of Action: Allows consumers to sue for statutory damages ($100-$750 per consumer per incident) in the event of unauthorized access, exfiltration, or disclosure resulting from failure to maintain reasonable security.",
        "tags": "privacy, data breach, california, cybersecurity, security, leak"
    },
    {
        "id": "stat_torts_281",
        "title": "Restatement (Second) of Torts - Elements of Negligence",
        "section": "Restatement (Second) of Torts § 281 et seq.",
        "jurisdiction": "Common Law / Multi-state",
        "description": "Defines the essential elements of a cause of action for negligence under US common law.",
        "provisions": "1. Elements of Negligence: A plaintiff must establish: (a) a duty of care, (b) a breach of that duty, (c) a causal connection, and (d) actual loss or damage.\n2. Standard of Care: The standard is that of a reasonable person under like circumstances.",
        "tags": "negligence, medical malpractice, duty of care, liability, damages, injury"
    }
]

def seed_database():
    """Seeds the local persistent ChromaDB instance with case law and statutes."""
    print("═" * 80)
    print("               COUNSELCORE DATABASE INGESTION & SEEDING ENGINE                ")
    print("═" * 80)
    
    # 1. Reset database folder if we want a fresh seed
    if os.path.exists(DB_DIR):
        print(f"[*] Removing existing database directory: {DB_DIR}")
        try:
            shutil.rmtree(DB_DIR)
        except Exception as e:
            print(f"[!] Warning: Could not fully delete database directory: {e}")

    # 2. Instantiate Chroma DB Client
    print(f"[*] Initializing persistent Chroma Client at: {DB_DIR}")
    client = chromadb.PersistentClient(path=DB_DIR)
    
    # 3. Use default embedding function
    # Chroma default uses SentenceTransformers "all-MiniLM-L6-v2" under the hood
    embedding_func = embedding_functions.DefaultEmbeddingFunction()

    # 4. Ingest Case Law Collection
    print("\n[*] Loading Case Law Collection...")
    case_collection = client.create_collection(
        name="case_law",
        embedding_function=embedding_func
    )
    
    case_docs = []
    case_metas = []
    case_ids = []
    
    for case in CASES:
        # Full text document for vector embedding
        full_text = f"""
Case Name: {case['name']}
Citation: {case['citation']}
Court: {case['court']}
Year: {case['year']}
Jurisdiction: {case['jurisdiction']}
Facts: {case['facts']}
Holding: {case['holding']}
Principle: {case['principle']}
Tags: {case['tags']}
"""
        case_docs.append(full_text)
        case_metas.append({
            "name": case["name"],
            "citation": case["citation"],
            "court": case["court"],
            "year": case["year"],
            "jurisdiction": case["jurisdiction"],
            "facts": case["facts"],
            "holding": case["holding"],
            "principle": case["principle"],
            "tags": case["tags"]
        })
        case_ids.append(case["id"])
        print(f"  ▸ Staged Case: {case['name']} ({case['year']})")

    case_collection.add(
        documents=case_docs,
        metadatas=case_metas,
        ids=case_ids
    )
    print(f"[✓] Successfully ingested {len(case_ids)} landmark cases into ChromaDB!")

    # 5. Ingest Statutes Collection
    print("\n[*] Loading Statutes Collection...")
    statutes_collection = client.create_collection(
        name="statutes",
        embedding_function=embedding_func
    )

    stat_docs = []
    stat_metas = []
    stat_ids = []

    for stat in STATUTES:
        full_text = f"""
Statute Title: {stat['title']}
Section: {stat['section']}
Jurisdiction: {stat['jurisdiction']}
Description: {stat['description']}
Provisions: {stat['provisions']}
Tags: {stat['tags']}
"""
        stat_docs.append(full_text)
        stat_metas.append({
            "title": stat["title"],
            "section": stat["section"],
            "jurisdiction": stat["jurisdiction"],
            "description": stat["description"],
            "provisions": stat["provisions"],
            "tags": stat["tags"]
        })
        stat_ids.append(stat["id"])
        print(f"  ▸ Staged Statute: {stat['title']} ({stat['section']})")

    statutes_collection.add(
        documents=stat_docs,
        metadatas=stat_metas,
        ids=stat_ids
    )
    print(f"[✓] Successfully ingested {len(stat_ids)} landmark statutes into ChromaDB!")
    print("\n" + "═" * 80)
    print("                    DATABASE INGESTION COMPLETED SUCCESSFULLY                 ")
    print("═" * 80)

if __name__ == "__main__":
    seed_database()
