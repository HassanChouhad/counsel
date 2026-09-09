import unittest
import os
from unittest.mock import patch, MagicMock

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from tools import search_case_law, lookup_statutes, draft_legal_brief
from strands import Agent
from strands.models import BedrockModel

class TestCounselCore(unittest.TestCase):
    
    def test_search_case_law_matches(self):
        """Test that searching case law with a known keyword returns matching cases."""
        results = search_case_law(query="non-compete", jurisdiction="California")
        self.assertTrue(len(results) > 0)
        # Ensure at least one returned case has the keyword or is the fallback
        self.assertTrue(any("non-compete" in case["facts"].lower() or "non-compete" in [t.lower() for t in case["tags"]] for case in results))

    def test_lookup_statutes_matches(self):
        """Test that looking up statutes with a known topic returns matching statutes."""
        results = lookup_statutes(topic="non-compete")
        self.assertTrue(len(results) > 0)
        # Ensure at least one returned statute has the keyword or is the fallback
        self.assertTrue(any("non-compete" in statute["description"].lower() or "non-compete" in [t.lower() for t in statute["tags"]] for statute in results))

    def test_draft_legal_brief(self):
        """Test that drafting a legal brief combines facts, precedents, and statutes into markdown."""
        case_facts = "The employee signed a California non-compete clause."
        precedents = search_case_law(query="non-compete", jurisdiction="California")
        statutes = lookup_statutes(topic="non-compete")
        
        brief = draft_legal_brief(case_facts, precedents, statutes)
        
        self.assertIn("COUNSELCORE", brief)
        self.assertIn("CONFIDENTIAL // ATTORNEY-CLIENT PRIVILEGE", brief)
        self.assertIn("California", brief)
        self.assertIn("non-compete", brief.lower())

    @patch('strands.models.BedrockModel')
    def test_agent_initialization(self, mock_bedrock_model):
        """Test that the Agent class can be initialized without prompt-related errors."""
        mock_model = mock_bedrock_model.return_value
        system_prompt = "You are a legal research assistant."
        
        # This is where the original error happened due to the 'prompt' parameter
        agent = Agent(
            model=mock_model,
            tools=[search_case_law, lookup_statutes, draft_legal_brief],
            system_prompt=system_prompt
        )
        
        self.assertIsNotNone(agent)

if __name__ == '__main__':
    unittest.main()
