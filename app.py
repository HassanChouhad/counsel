#!/usr/bin/env python3
"""
CounselCore - Autonomous Legal Research Agent
==============================================
Main entry point for the AWS AI Agents Hackathon submission.
This application integrates AWS Bedrock with the Strands Agents SDK
to autonomously ingest case facts, execute legal research across statutory
and precedent databases, and compile a structured legal strategy brief.

Usage:
  python app.py
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ANSI Escape Sequences for Terminal Styling
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"


def print_banner():
    """Prints a beautiful CLI banner for the hackathon presentation."""
    banner = f"""
{BLUE}{BOLD}================================================================================
  ______                                  _  ______               
 / _____)                                | |/ _____)              
| /       ___  _   _ ____   ___ _____  | | /      ___   ____ _____ 
| |      / _ \| | | |  _ \ /___) ___ | | | |     / _ \ / ___| ___ |
| \_____| |_| | |_| | | | |___ | ____| | | \_____| |_| | |   | ____|
 \______)\___/|____/|_| |_(___/|_____)  \_)______)\___/|_|   |_____)
                                                                  
                      AUTONOMOUS LEGAL RESEARCH AGENT
================================================================================{RESET}
{CYAN}Track: Professional Agents{RESET} | {MAGENTA}Powered by AWS Bedrock & Strands Agents SDK{RESET}
"""
    print(banner)


def check_aws_credentials():
    """
    Validates that necessary AWS credentials and configuration exist in the environment.
    Provides clear, actionable troubleshooting steps if keys are missing.
    """
    aws_keys = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"]
    missing_keys = [key for key in aws_keys if not os.getenv(key)]

    if missing_keys:
        print(f"\n{RED}{BOLD}⚠️  CONFIGURATION ERROR: Missing AWS Credentials{RESET}")
        print(f"{YELLOW}The following environment variables are missing from your environment or .env file:{RESET}")
        for key in missing_keys:
            print(f"  - {BOLD}{key}{RESET}")
        
        print(f"\n{GREEN}{BOLD}To run CounselCore, please configure your AWS environment using one of these methods:{RESET}")
        print(f"1. Create a {BOLD}.env{RESET} file in the root of this project containing:")
        print(f"   {CYAN}AWS_ACCESS_KEY_ID=your_access_key_id{RESET}")
        print(f"   {CYAN}AWS_SECRET_ACCESS_KEY=your_secret_access_key{RESET}")
        print(f"   {CYAN}AWS_DEFAULT_REGION=us-east-1{RESET}")
        print("2. Export them directly in your shell:")
        print(f"   {CYAN}export AWS_ACCESS_KEY_ID=\"your_key_id\"{RESET}")
        print(f"   {CYAN}export AWS_SECRET_ACCESS_KEY=\"your_secret\"{RESET}")
        print(f"   {CYAN}export AWS_DEFAULT_REGION=\"us-east-1\"{RESET}")
        
        print(f"\n{YELLOW}Note: CounselCore relies on Amazon Bedrock models (e.g., Claude 3 Sonnet).{RESET}")
        print(f"Please ensure your AWS account has model access granted in the Bedrock console.")
        print("-" * 80)
        return False
    return True


def run_agent_loop():
    """Initializes the Strands Agent and manages the interactive terminal loop."""
    print(f"\n{GREEN}[*] Initializing CounselCore Agent engine...{RESET}")
    
    # Delayed imports to handle dependency checks and error boundaries gracefully
    try:
        from strands import Agent
        from strands.models import BedrockModel
        from tools import search_case_law, lookup_statutes, draft_legal_brief
    except ImportError as e:
        print(f"\n{RED}{BOLD}❌ IMPORT ERROR: Failed to load required packages.{RESET}")
        print(f"Please ensure you have installed the project requirements using:")
        print(f"  {CYAN}pip install -r requirements.txt{RESET}")
        print(f"Detail: {e}")
        sys.exit(1)

    try:
        # Initialize AWS Bedrock Model (Claude 3 Sonnet)
        # Using anthropic.claude-3-sonnet-20240229-v1:0 as requested for standard compatibility
        model_id = os.getenv("AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        
        print(f"{GREEN}[*] Connecting to Amazon Bedrock with Model ID: {RESET}{BOLD}{model_id}{RESET}")
        model = BedrockModel(model_id=model_id)

        # Set up a structured, role-specific system prompt to instruct the Strands Agent
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

        # Initialize the Strands Agent with the model, toolbelt, and prompt
        agent = Agent(
            model=model,
            tools=[search_case_law, lookup_statutes, draft_legal_brief],
            system_prompt=system_prompt
        )
        print(f"{GREEN}[✓] CounselCore Agent initialized successfully and ready for inquiry.{RESET}")
        print("=" * 80)

    except Exception as e:
        print(f"\n{RED}{BOLD}❌ ERROR: Failed to initialize AWS Bedrock or Strands SDK.{RESET}")
        print(f"Error Details: {e}")
        print(f"{YELLOW}Please double-check your AWS credentials, internet connection, and Bedrock model access permissions.{RESET}")
        sys.exit(1)

    # Main Interactive Terminal Loop
    while True:
        print(f"\n{BLUE}{BOLD}--- ENTER CASE FACTS & RESEARCH PARAMETERS ---{RESET}")
        print("Please enter or paste your case notes, client interview facts, or legal dispute details below.")
        print(f"{YELLOW}Type 'DONE' on a new line or press Ctrl+D (Ctrl+Z on Windows) when you are finished pasting.{RESET}")
        print("-" * 60)

        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "DONE":
                    break
                lines.append(line)
        except EOFError:
            pass

        case_facts = "\n".join(lines).strip()

        if not case_facts:
            print(f"{RED}Error: Case facts cannot be empty. Please try again.{RESET}")
            continue

        print(f"\n{BLUE}[*] Launching CounselCore Autonomous Pipeline...{RESET}")
        
        # Simulating active pipeline phases to illustrate agentic reasoning
        print(f"    {CYAN}▸ Phase 1/4: Analyzing factual matrix and isolating legal themes...{RESET}")
        time.sleep(1)
        print(f"    {CYAN}▸ Phase 2/4: Querying statutory database for regulatory authority...{RESET}")
        time.sleep(1.2)
        print(f"    {CYAN}▸ Phase 3/4: Retrieving judicial precedents and holdings...{RESET}")
        time.sleep(1.2)
        print(f"    {CYAN}▸ Phase 4/4: Triggering LLM reasoning and compiling legal brief...{RESET}\n")

        try:
            # Execute the agent autonomously
            # Strands Agent handles tool selecting, calling, and compiling the outputs internally
            response = agent(case_facts)

            print(f"\n{GREEN}{BOLD}================================================================================{RESET}")
            print(f"{GREEN}{BOLD}                        GENERATED LEGAL BRIEF & STRATEGY                        {RESET}")
            print(f"{GREEN}{BOLD}================================================================================{RESET}\n")
            print(response)
            print(f"\n{GREEN}{BOLD}================================================================================{RESET}")
            
        except Exception as e:
            print(f"\n{RED}{BOLD}❌ RUNTIME ERROR: The agent failed to complete the request.{RESET}")
            print(f"Error Details: {e}")
            print(f"{YELLOW}If this is an AWS API or credentials error, please review your .env file or AWS IAM permissions.{RESET}")

        # Prompt for another run
        try:
            choice = input(f"\n{BOLD}Would you like to analyze another case? (y/N): {RESET}").strip().lower()
            if choice not in ["y", "yes"]:
                print(f"\n{BLUE}Thank you for choosing CounselCore!{RESET}\n")
                break
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{BLUE}Exiting CounselCore. Goodbye!{RESET}\n")
            break


def main():
    """Main application entry point."""
    print_banner()
    if check_aws_credentials():
        run_agent_loop()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
