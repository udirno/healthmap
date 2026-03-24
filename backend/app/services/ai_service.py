import anthropic
from typing import Dict, Any, List
from app.config import settings

class AIService:

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def generate_insight(
        self,
        question: str,
        disease_data: Dict[str, Any] = None,
        climate_data: Dict[str, Any] = None,
        correlation_data: List[Dict[str, Any]] = None,
        economic_data: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate AI insight using Claude with conversation context"""

        # Build context
        context_parts = []

        if disease_data:
            context_parts.append(f"Disease Data: {disease_data}")

        if climate_data:
            context_parts.append(f"Climate Data: {climate_data}")

        if correlation_data:
            context_parts.append(f"Correlation Analysis: {correlation_data}")

        if economic_data:
            context_parts.append(f"Economic/Socioeconomic Data: {economic_data}")

        context = "\n\n".join(context_parts)

        # Build prompt
        system_prompt = """You are an expert epidemiologist and data scientist specializing in global health intelligence.

Your role is to analyze disease patterns, environmental factors, and socioeconomic data to provide clear, evidence-based insights.

Guidelines:
- Provide concise, readable explanations (2-4 paragraphs maximum)
- Always acknowledge uncertainty and data limitations
- Distinguish correlation from causation
- Use specific numbers and trends from the data
- Avoid medical advice or diagnostic claims
- Suggest potential factors but frame as hypotheses
- Be scientifically rigorous but accessible to non-experts
- Reference previous conversation context when relevant

Your response should be structured as:
1. Direct answer to the question
2. Supporting evidence from the data
3. Potential explanations or contributing factors
4. Important caveats or limitations"""

        user_prompt = f"""Question: {question}

Available Data:
{context}

Please provide a clear, evidence-based insight that answers this question."""

        # Build messages array with conversation history
        messages = []

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current question
        messages.append({"role": "user", "content": user_prompt})

        # Call Claude
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            return f"Error generating insight: {str(e)}"

    def generate_comparison_insight(
        self,
        regions: List[str],
        disease: str,
        comparison_data: Dict[str, Any]
    ) -> str:
        """Generate comparative analysis between regions"""

        system_prompt = """You are an expert epidemiologist analyzing disease patterns across different regions.

Provide a clear comparative analysis highlighting:
- Key differences in disease burden
- Potential explanations for differences
- Environmental or socioeconomic factors that may contribute
- Important trends or patterns

Be concise (2-3 paragraphs) and evidence-based."""

        user_prompt = f"""Compare {disease} patterns across these regions: {', '.join(regions)}

Data:
{comparison_data}

Provide a comparative analysis."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Error generating comparison: {str(e)}"
