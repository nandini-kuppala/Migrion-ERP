"""Gemini AI Agent wrapper for various migration tasks."""
import json
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from src.utils.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE
from src.utils.helpers import setup_logger

logger = setup_logger("gemini_agent")


class GeminiAgent:
    """Base class for Gemini AI agents."""

    def __init__(self, api_key: str = GEMINI_API_KEY):
        """Initialize Gemini agent."""
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.temperature = GEMINI_TEMPERATURE

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from Gemini."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', self.temperature),
                    max_output_tokens=kwargs.get('max_output_tokens', 2048),
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error: {str(e)}"

    def generate_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate JSON response from Gemini."""
        full_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
        response_text = self.generate(full_prompt, **kwargs)

        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return {"error": "Failed to parse JSON response", "raw_response": response_text}


class PlannerAgent(GeminiAgent):
    """Agent for generating migration plans."""

    def generate_migration_plan(
        self,
        org_info: Dict[str, Any],
        legacy_system: str,
        target_erp: str,
        data_volume: str
    ) -> Dict[str, Any]:
        """Generate detailed migration plan."""
        prompt = f"""
You are an expert ERP migration planner. Generate a comprehensive migration plan.

Organization: {org_info.get('company_name', 'Unknown')}
Industry: {org_info.get('industry', 'Unknown')}
Legacy System: {legacy_system}
Target ERP: {target_erp}
Data Volume: {data_volume}

Generate a detailed migration plan with the following structure:
{{
  "plan_id": "unique identifier",
  "overview": "executive summary",
  "phases": [
    {{
      "phase_name": "string",
      "duration_days": number,
      "description": "string",
      "critical_steps": ["step1", "step2"],
      "risks": ["risk1", "risk2"],
      "success_criteria": ["criteria1"]
    }}
  ],
  "estimated_total_duration_days": number,
  "estimated_downtime_hours": number,
  "risk_assessment": {{
    "overall_risk_level": "Low/Medium/High",
    "major_risks": ["risk1", "risk2"],
    "mitigation_strategies": ["strategy1", "strategy2"]
  }},
  "resource_requirements": {{
    "team_size": number,
    "skillsets_needed": ["skill1", "skill2"],
    "tools_required": ["tool1", "tool2"]
  }},
  "validation_checkpoints": ["checkpoint1", "checkpoint2"],
  "rollback_strategy": "description of rollback approach"
}}
"""
        return self.generate_json(prompt)


class MapperAgent(GeminiAgent):
    """Agent for schema mapping."""

    def generate_mappings(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        sample_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate field mappings between schemas."""
        prompt = f"""
You are an expert data mapper. Analyze the source and target schemas and generate field mappings.

Source Schema:
{json.dumps(source_schema, indent=2)}

Target Schema:
{json.dumps(target_schema, indent=2)}

{f"Sample Data: {json.dumps(sample_data[:5], indent=2)}" if sample_data else ""}

Generate mappings with the following structure:
{{
  "mappings": [
    {{
      "source_field": "string",
      "target_field": "string",
      "transform": "transformation logic or 'direct' if no transformation",
      "confidence": float between 0 and 1,
      "explanation": "reason for this mapping",
      "data_type_source": "string",
      "data_type_target": "string",
      "requires_validation": boolean
    }}
  ],
  "unmapped_source_fields": ["field1", "field2"],
  "unmapped_target_fields": ["field1", "field2"],
  "suggested_transformations": [
    {{
      "field": "string",
      "transformation": "description",
      "reason": "explanation"
    }}
  ]
}}
"""
        return self.generate_json(prompt)


class QualityAgent(GeminiAgent):
    """Agent for data quality analysis."""

    def analyze_quality_report(
        self,
        quality_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from quality metrics."""
        prompt = f"""
You are a data quality expert. Analyze the following quality metrics and provide insights.

Quality Metrics:
{json.dumps(quality_metrics, indent=2)}

Generate analysis with this structure:
{{
  "overall_assessment": "High/Medium/Low quality",
  "quality_score": float between 0 and 1,
  "key_findings": ["finding1", "finding2"],
  "critical_issues": ["issue1", "issue2"],
  "recommendations": [
    {{
      "issue": "string",
      "recommendation": "string",
      "priority": "High/Medium/Low",
      "estimated_effort": "string"
    }}
  ],
  "data_readiness": "Ready/Needs Work/Not Ready",
  "estimated_cleanup_time": "string"
}}
"""
        return self.generate_json(prompt)


class OptimizerAgent(GeminiAgent):
    """Agent for migration strategy optimization."""

    def recommend_strategy(
        self,
        data_size_gb: float,
        acceptable_downtime_hours: float,
        concurrent_users: int,
        budget_usd: float = None
    ) -> Dict[str, Any]:
        """Recommend optimal migration strategy."""
        prompt = f"""
You are a cloud migration expert. Recommend the best migration strategy.

Parameters:
- Data Size: {data_size_gb} GB
- Acceptable Downtime: {acceptable_downtime_hours} hours
- Concurrent Users: {concurrent_users}
{f"- Budget: ${budget_usd:,.2f}" if budget_usd else "- Budget: Not specified"}

Generate recommendation with this structure:
{{
  "recommended_strategy": "Big Bang/Phased/Hybrid/Parallel Run",
  "expected_downtime_hours": number,
  "risk_level": "Low/Medium/High",
  "estimated_cost_usd": number,
  "rationale": "detailed explanation",
  "implementation_steps": ["step1", "step2"],
  "alternative_strategies": [
    {{
      "strategy": "string",
      "pros": ["pro1", "pro2"],
      "cons": ["con1", "con2"],
      "estimated_downtime_hours": number,
      "risk_level": "Low/Medium/High"
    }}
  ],
  "mitigation_plan": ["action1", "action2"],
  "success_metrics": ["metric1", "metric2"]
}}
"""
        return self.generate_json(prompt)


class AuditorAgent(GeminiAgent):
    """Agent for audit and compliance checking."""

    def generate_audit_report(
        self,
        transformations: List[Dict[str, Any]],
        compliance_requirements: List[str]
    ) -> Dict[str, Any]:
        """Generate audit report for transformations."""
        prompt = f"""
You are a compliance and audit expert. Review transformations and generate an audit report.

Transformations:
{json.dumps(transformations[:10], indent=2)}  # Limit to first 10

Compliance Requirements:
{json.dumps(compliance_requirements, indent=2)}

Generate report with this structure:
{{
  "audit_summary": "overall summary",
  "compliance_status": "Compliant/Partial/Non-Compliant",
  "findings": [
    {{
      "category": "string",
      "severity": "Critical/High/Medium/Low",
      "description": "string",
      "affected_fields": ["field1"],
      "recommendation": "string"
    }}
  ],
  "pii_concerns": [
    {{
      "field": "string",
      "concern": "string",
      "mitigation": "string"
    }}
  ],
  "gdpr_compliance": {{
    "status": "Compliant/Non-Compliant",
    "issues": ["issue1"],
    "required_actions": ["action1"]
  }},
  "recommendations": ["recommendation1", "recommendation2"],
  "approval_status": "Approved/Conditional/Rejected"
}}
"""
        return self.generate_json(prompt)


class ValidationAgent(GeminiAgent):
    """Agent for data validation."""

    def suggest_validation_rules(
        self,
        schema: Dict[str, Any],
        sample_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Suggest validation rules for schema."""
        prompt = f"""
You are a data validation expert. Suggest validation rules for the given schema.

Schema:
{json.dumps(schema, indent=2)}

{f"Sample Data: {json.dumps(sample_data[:5], indent=2)}" if sample_data else ""}

Generate validation rules with this structure:
{{
  "validation_rules": [
    {{
      "field": "string",
      "rule_type": "required/format/range/custom",
      "rule": "description of validation rule",
      "error_message": "string",
      "severity": "Critical/High/Medium/Low"
    }}
  ],
  "data_quality_checks": [
    {{
      "check_name": "string",
      "description": "string",
      "expected_result": "string"
    }}
  ],
  "transformation_validations": ["validation1", "validation2"]
}}
"""
        return self.generate_json(prompt)
