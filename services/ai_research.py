"""
AI-Powered Research Service using Claude/OpenAI
Provides intelligent analysis, entity extraction, and insights
"""
import os
import logging
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)


class AIResearchService:
    """
    Advanced AI research service using Claude or OpenAI
    Provides intelligent genealogy analysis and entity extraction
    """

    def __init__(self, provider=None, api_key=None):
        """
        Initialize AI service

        Args:
            provider: 'anthropic' or 'openai' (defaults to config)
            api_key: API key (defaults to config)
        """
        from config import Config

        self.provider = provider or Config.AI_PROVIDER
        self.api_key = api_key or (Config.ANTHROPIC_API_KEY if self.provider == 'anthropic' else Config.OPENAI_API_KEY)
        self.model = Config.AI_MODEL
        self.max_tokens = Config.AI_MAX_TOKENS

        # Initialize client
        if self.provider == 'anthropic':
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key) if self.api_key else None
            except ImportError:
                logger.warning("Anthropic package not installed")
                self.client = None
        elif self.provider == 'openai':
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key) if self.api_key else None
            except ImportError:
                logger.warning("OpenAI package not installed")
                self.client = None
        else:
            self.client = None

    def _call_ai(self, prompt: str, system_prompt: str = None) -> str:
        """
        Call AI model with prompt

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)

        Returns:
            str: AI response
        """
        if not self.client or not self.api_key:
            logger.warning("AI client not initialized - using fallback")
            return self._fallback_response(prompt)

        try:
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_prompt if system_prompt else "You are an expert genealogist and skip tracer.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text

            elif self.provider == 'openai':
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model=self.model or "gpt-4-turbo-preview",
                    max_tokens=self.max_tokens,
                    messages=messages
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Fallback when AI is not available"""
        return json.dumps({
            "status": "ai_unavailable",
            "message": "AI analysis not available - API key required"
        })

    def analyze_person_data(self, sources_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze person data from multiple sources using AI

        Args:
            sources_data: Dictionary of data from various sources

        Returns:
            dict: AI analysis with insights
        """
        system_prompt = """You are an expert genealogist and skip tracer. Analyze the provided data and:
1. Identify the most likely current contact information
2. Determine family relationships and connections
3. Assess data quality and confidence levels
4. Flag any inconsistencies or concerns
5. Provide actionable recommendations

Return your analysis as structured JSON."""

        prompt = f"""Analyze this genealogy data and provide comprehensive insights:

Data from sources:
{json.dumps(sources_data, indent=2)}

Provide a structured analysis with:
- confidence_score (0-100): Overall confidence in the data
- primary_identity: Most likely correct personal information
- family_relationships: Identified family members with confidence scores
- contact_info: Best contact information (addresses, phones, emails) ranked by likelihood
- data_quality_issues: Any concerns or inconsistencies
- recommendations: Next steps for verification
- heir_likelihood: If this person could be an heir (and why)

Format as JSON."""

        response = self._call_ai(prompt, system_prompt)

        try:
            # Try to parse as JSON
            return json.loads(response)
        except:
            # If not valid JSON, structure it
            return {
                'analysis': response,
                'confidence_score': 50.0,
                'structured': False
            }

    def analyze_document(self, text: str, document_type: str = 'unknown') -> Dict[str, Any]:
        """
        AI analysis of document text

        Args:
            text: Document text
            document_type: Type of document

        Returns:
            dict: Extracted entities and analysis
        """
        system_prompt = """You are an expert in legal document analysis, genealogy, and property records.
Extract all relevant information from documents and structure it for skip tracing purposes."""

        prompt = f"""Analyze this {document_type} document and extract all relevant information:

DOCUMENT TEXT:
{text[:8000]}  # Limit to first 8000 chars

Extract and return as JSON:
{{
  "document_type": "identified type",
  "summary": "brief summary",
  "people": [
    {{
      "name": "Full Name",
      "role": "decedent/heir/spouse/etc",
      "dates": {{"birth": "YYYY-MM-DD", "death": "YYYY-MM-DD"}},
      "confidence": 0-100
    }}
  ],
  "properties": [
    {{
      "address": "full address",
      "value": "estimated value",
      "ownership": "details"
    }}
  ],
  "relationships": [
    {{
      "person1": "Name",
      "person2": "Name",
      "relationship": "son/daughter/spouse/etc",
      "confidence": 0-100
    }}
  ],
  "financial_info": ["any amounts or financial details"],
  "dates": ["important dates found"],
  "locations": ["cities, counties, states"],
  "phone_numbers": ["formatted phone numbers"],
  "addresses": ["full addresses"],
  "key_facts": ["important facts for heir tracing"],
  "confidence": 0-100
}}"""

        response = self._call_ai(prompt, system_prompt)

        try:
            return json.loads(response)
        except:
            return {
                'raw_analysis': response,
                'structured': False,
                'confidence': 30.0
            }

    def natural_language_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process natural language queries about genealogy/property data

        Args:
            query: Natural language question
            context: Optional context (property/person data)

        Returns:
            dict: AI response with structured answer
        """
        system_prompt = """You are an AI assistant for a skip tracing and genealogy platform.
Answer questions about properties, heirs, and genealogy research.
Provide clear, actionable answers."""

        context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}" if context else ""

        prompt = f"""User Question: {query}{context_str}

Provide a clear answer with:
- Direct answer to the question
- Relevant data points
- Confidence level
- Recommended next actions

Format as JSON with keys: answer, confidence, data_points, recommendations"""

        response = self._call_ai(prompt, system_prompt)

        try:
            return json.loads(response)
        except:
            return {
                'answer': response,
                'confidence': 50.0,
                'structured': False
            }

    def identify_heirs(self, deceased_name: str, family_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use AI to identify likely heirs from family data

        Args:
            deceased_name: Name of deceased property owner
            family_data: Family tree and relationship data

        Returns:
            list: Ranked list of potential heirs with scores
        """
        system_prompt = """You are an expert in inheritance law and genealogy.
Analyze family data to identify legal heirs according to intestate succession laws.
Consider relationship proximity, survival, and legal factors."""

        prompt = f"""Identify potential heirs for: {deceased_name}

Family Data:
{json.dumps(family_data, indent=2)}

For each potential heir, provide:
{{
  "name": "Full Name",
  "relationship": "relationship to deceased",
  "relationship_degree": 1-10 (1=child, 2=grandchild, etc),
  "heir_probability": 0-100,
  "intestate_share": "estimated % of estate",
  "reasoning": "why they are/aren't likely heir",
  "verification_needed": ["what to verify"],
  "confidence": 0-100
}}

Return as JSON array, ranked by heir_probability.
Consider:
- Direct descendants have priority
- Surviving spouse rights
- State intestacy laws (assume general US law)
- Per stirpes distribution"""

        response = self._call_ai(prompt, system_prompt)

        try:
            result = json.loads(response)
            return result if isinstance(result, list) else result.get('heirs', [])
        except:
            return []

    def score_heir_likelihood(self, heir_data: Dict[str, Any], property_data: Dict[str, Any]) -> float:
        """
        AI-powered heir likelihood scoring

        Args:
            heir_data: Information about potential heir
            property_data: Property and owner information

        Returns:
            float: Confidence score 0-100
        """
        system_prompt = """Calculate heir likelihood score based on available evidence.
Consider relationship proximity, data quality, verification status, and legal factors."""

        prompt = f"""Score this potential heir:

Heir Data:
{json.dumps(heir_data, indent=2)}

Property/Deceased Data:
{json.dumps(property_data, indent=2)}

Return JSON with:
{{
  "confidence_score": 0-100,
  "factors": {{
    "relationship_strength": 0-100,
    "data_quality": 0-100,
    "verification_level": 0-100,
    "legal_validity": 0-100
  }},
  "reasoning": "explanation",
  "red_flags": ["any concerns"],
  "next_steps": ["verification recommendations"]
}}"""

        response = self._call_ai(prompt, system_prompt)

        try:
            result = json.loads(response)
            return result.get('confidence_score', 50.0)
        except:
            return 50.0

    def generate_research_report(self, property_id: int) -> str:
        """
        Generate comprehensive AI research report

        Args:
            property_id: Property ID to report on

        Returns:
            str: Formatted report text
        """
        from models import Property, Heir

        property_obj = Property.query.get(property_id)
        if not property_obj:
            return "Property not found"

        heirs = Heir.query.filter_by(property_id=property_id).all()

        data = {
            'property': property_obj.to_dict(),
            'heirs': [h.to_dict() for h in heirs]
        }

        system_prompt = """Generate professional skip tracing reports.
Include executive summary, findings, heir analysis, and recommendations."""

        prompt = f"""Generate a comprehensive skip tracing report for this property and heirs:

{json.dumps(data, indent=2)}

Create a professional report with:
1. Executive Summary
2. Property Details
3. Heir Analysis (ranked by probability)
4. Verification Status
5. Recommendations
6. Next Actions

Format as markdown."""

        return self._call_ai(prompt, system_prompt)
