#!/usr/bin/env python3
"""
api.py
================================================================================
The REST API server backend for CounselCore. Exposes endpoints to check health
and submit case facts for autonomous research, bridging the React web frontend
with our Strands SDK Agent engine.
================================================================================
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environmental configurations
load_dotenv()

app = FastAPI(
    title="CounselCore API Server",
    description="REST API wrapping the autonomous legal research agent engine.",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS) for development/review
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    facts: str

@app.get("/api/health")
def health_check():
    """Simple status probe used by the frontend to auto-detect backend availability."""
    return {"status": "ok", "message": "CounselCore Agent API Server is healthy and online."}

@app.post("/api/research")
def conduct_research(request: ResearchRequest):
    """
    Ingests raw case facts, runs the Strands Agent pipeline synchronously,
    and returns the fully synthesized legal strategy brief.
    """
    facts_stripped = request.facts.strip()
    if not facts_stripped:
        raise HTTPException(status_code=400, detail="Case facts cannot be empty.")

    try:
        from strands import Agent
        from strands.models import BedrockModel
        from tools import search_case_law, lookup_statutes, draft_legal_brief

        # Connect to Bedrock Model
        model_id = os.getenv("AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        print(f"[*] API Client connecting to Bedrock model: {model_id}")
        model = BedrockModel(model_id=model_id)

        # Retrieve system prompt configuration
        system_prompt = """
You are CounselCore, an elite autonomous legal research agent. Your core objective is to analyze case facts, identify key legal issues, perform targeted statutory and precedent searches using your tools, and synthesize your findings into a comprehensive Legal Strategy Brief.

When a user provides case notes or facts:
1. Carefully parse the input to determine the core legal categories (e.g., employment contracts, intellectual property, medical malpractice, cyber privacy) and any jurisdictions involved.
2. Call the 'lookup_statutes' tool to retrieve relevant statutory codes and laws based on the topics identified.
3. Call the 'search_case_law' tool using appropriate keywords and jurisdictional filters to retrieve governing judicial precedents.
4. Collect all factual backgrounds and search results, and pass them to 'draft_legal_brief'.
5. Once 'draft_legal_brief' returns the structured markdown document, present it to the user as your final output. Do not truncate, summarize, or alter the draft's formatting unless requested.

Always remain objective, thorough, and analytical. Act as an expert paralegal supporting a senior trial lawyer.
"""

        # Instantiate Strands Agent with ChromaDB-backed tools
        agent = Agent(
            model=model,
            tools=[search_case_law, lookup_statutes, draft_legal_brief],
            system_prompt=system_prompt
        )

        # Run the agent pipeline autonomously
        print(f"[*] Executing Agent reasoning for facts: {facts_stripped[:100]}...")
        brief = agent(facts_stripped)
        print("[✓] Strategy brief generated successfully!")
        
        return {"brief": str(brief)}

    except Exception as e:
        print(f"[!] Error executing legal agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Start on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
