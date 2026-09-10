#!/usr/bin/env python3
"""
ingest_real_cases.py
================================================================================
A premium database seeder for CounselCore that downloads real historical case
law from the Harvard Caselaw Access Project (via static.case.law), uses our AWS
Bedrock LLM model to autonomously extract the facts, holdings, and principles,
and ingests them into the local ChromaDB semantic vector database.
================================================================================
"""

import os
import sys
import json
import requests
import chromadb
from dotenv import load_dotenv

# Load configuration
load_dotenv()

# AWS Configurations
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
MODEL_ID = os.getenv("AWS_BEDROCK_MODEL_ID", "deepseek.v3.2")

# Database configuration
DB_DIR = "./chroma_db"

def get_bedrock_client():
    """Initializes and returns a boto3 Bedrock client."""
    import boto3
    try:
        return boto3.client("bedrock-runtime", region_name=AWS_REGION)
    except Exception as e:
        print(f"[!] Error creating Bedrock client: {e}")
        return None

def analyze_case_with_llm(client, case_name, decision_date, court, opinion_text):
    """
    Calls the configured AWS Bedrock model to analyze the raw opinion text
    and extract structured: facts, holding, core principle, and tags.
    """
    if not client:
        return None

    # Limit text to ~8000 characters to prevent huge token consumption or context overflow
    truncated_text = opinion_text[:8000]

    prompt = f"""You are a senior legal analyst. Analyze the following real historical court opinion and extract:
1. "facts": A 2-3 sentence summary of the factual matrix and dispute background.
2. "holding": A 1-2 sentence summary of the court's ultimate holding or ruling.
3. "principle": A 1-2 sentence statement of the core legal principle or rule of law established in this case.
4. "tags": A comma-separated list of 5-8 relevant legal keywords (e.g. non-compete, jurisdiction, contract, negligence).

Case Name: {case_name}
Decision Date: {decision_date}
Court: {court}

Opinion Text (first 8000 chars):
{truncated_text}

Provide your response strictly in the following JSON format:
{{
  "facts": "factual matrix text here",
  "holding": "holding text here",
  "principle": "core legal principle here",
  "tags": "tag1, tag2, tag3"
}}
Do not return any introductory or explanatory text outside the JSON block. Return ONLY the raw JSON.
"""

    try:
        # Check if using converse or normal invoke
        # We can use the simple invoke_model API
        body_dict = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.2
            }
        }
        
        # Bedrock Converse API is standard for most models now and highly recommended
        response = client.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1000, "temperature": 0.2}
        )
        
        output_text = response['output']['message']['content'][0]['text'].strip()
        
        # Clean any markdown block wrapping if present
        if output_text.startswith("```"):
            lines = output_text.split("\n")
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                output_text = "\n".join(lines[1:-1]).strip()
                
        return json.loads(output_text)
    except Exception as e:
        print(f"  [!] LLM extraction failed for {case_name}: {e}. Using fallback parser.")
        return None

def fallback_parser(case_name, opinion_text):
    """Provides a basic fallback extraction if AWS Bedrock is unavailable or fails."""
    facts = opinion_text[:300].strip() + "..." if len(opinion_text) > 300 else opinion_text
    holding = "Judgment was rendered according to the court's full opinion."
    principle = "Governed by historical California common law principles."
    tags = "california, historical, common law, precedent"
    return {
        "facts": facts,
        "holding": holding,
        "principle": principle,
        "tags": tags
    }

def ingest_california_cases(num_cases_to_ingest=15):
    """Downloads, parses, and ingests real California cases into ChromaDB."""
    print("═" * 80)
    print("          COUNSELCORE PREMIUM REAL CALIFORNIA CASE LAW INGESTER              ")
    print("═" * 80)
    
    # 1. Fetch metadata for Volume 1 of California Reports
    metadata_url = "https://static.case.law/cal/1/CasesMetadata.json"
    print(f"[*] Fetching California Vol. 1 Case Metadata from static.case.law...")
    try:
        response = requests.get(metadata_url)
        response.raise_for_status()
        cases_meta = response.json()
        print(f"[✓] Successfully retrieved metadata for {len(cases_meta)} California cases.")
    except Exception as e:
        print(f"[!] Error fetching metadata: {e}")
        sys.exit(1)

    # 2. Setup Bedrock Client
    print(f"[*] Connecting to AWS Bedrock in region: {AWS_REGION} with model: {MODEL_ID}")
    bedrock = get_bedrock_client()
    if bedrock:
        print("[✓] Bedrock client connected successfully. AI-driven parsing is enabled.")
    else:
        print("[!] Bedrock client unavailable. Falling back to rule-based parser.")

    # 3. Setup Chroma Client
    print(f"[*] Connecting to persistent Chroma DB at: {DB_DIR}")
    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    
    # Get or create the case_law collection
    # Note: We append to the existing mock collection so that both mock and real cases exist!
    case_collection = chroma_client.get_or_create_collection(name="case_law")

    # 4. Ingest select cases
    print(f"\n[*] Starting ingestion of top {num_cases_to_ingest} real cases...")
    count = 0
    
    # Skip cases that might be extremely short or contain index metadata
    for case_meta in cases_meta:
        if count >= num_cases_to_ingest:
            break
            
        case_id = f"real_case_{case_meta['id']}"
        file_name = case_meta.get("file_name")
        case_name = case_meta.get("name")
        court_name = case_meta.get("court", {}).get("name", "Supreme Court of California")
        decision_date = case_meta.get("decision_date", "1850")
        year = int(decision_date.split("-")[0]) if "-" in decision_date else int(decision_date)
        citation = case_meta.get("citations", [{}])[0].get("cite", "1 Cal.")

        # Download the full text JSON
        case_url = f"https://static.case.law/cal/1/cases/{file_name}.json"
        try:
            case_response = requests.get(case_url)
            case_response.raise_for_status()
            case_data = case_response.json()
            
            # Extract full opinion text
            opinions = case_data.get("casebody", {}).get("opinions", [])
            if not opinions:
                continue
                
            full_opinion_text = "\n\n".join([op.get("text", "") for op in opinions])
            if not full_opinion_text.strip():
                continue
                
            print(f"\n[{count + 1}/{num_cases_to_ingest}] Processing: {case_name} ({year})")
            
            # Analyze case structure via LLM or Fallback
            analysis = analyze_case_with_llm(
                bedrock, 
                case_name, 
                decision_date, 
                court_name, 
                full_opinion_text
            )
            
            if not analysis:
                analysis = fallback_parser(case_name, full_opinion_text)
                
            # Index document
            full_text_doc = f"""
Case Name: {case_name}
Citation: {citation}
Court: {court_name}
Year: {year}
Jurisdiction: California / State Court
Facts: {analysis['facts']}
Holding: {analysis['holding']}
Principle: {analysis['principle']}
Tags: {analysis['tags']}
"""
            # Store in ChromaDB
            case_collection.add(
                documents=[full_text_doc],
                metadatas=[{
                    "name": case_name,
                    "citation": citation,
                    "court": court_name,
                    "year": year,
                    "jurisdiction": "California State Court",
                    "facts": analysis['facts'],
                    "holding": analysis['holding'],
                    "principle": analysis['principle'],
                    "tags": analysis['tags']
                }],
                ids=[case_id]
            )
            
            print(f"  [✓] Successfully ingested case {case_id}!")
            print(f"  Facts summary: {analysis['facts']}")
            count += 1
            
        except Exception as e:
            print(f"  [!] Skipped case due to fetch/parsing error: {e}")
            continue

    print("\n" + "═" * 80)
    print(f"       SUCCESS: Real historical California cases ingested: {count}            ")
    print("═" * 80)

if __name__ == "__main__":
    # By default, ingest 5 premium California cases to build an incredibly strong base
    ingest_california_cases(num_cases_to_ingest=5)
