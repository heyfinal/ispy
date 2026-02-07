"""
iSpy AI Engine - OpenAI or Gemini Integration for Intelligent Analysis
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .constants import AI_DEFAULT_MODEL, AI_MAX_LOG_CHARS, AI_MAX_TOKENS, AI_MAX_CONTEXT_CHARS
from .device import DeviceInfo


@dataclass
class AIAnalysisResult:
    """Result from AI analysis"""
    success: bool
    summary: str
    severity: str  # Low, Medium, High, Critical
    issues: List[str]
    recommendations: List[str]
    root_causes: List[str]
    raw_response: Optional[str] = None
    error: Optional[str] = None


class AIEngine:
    """AI-powered analysis engine using OpenAI or Gemini"""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        openai_model: Optional[str] = None,
        gemini_model: Optional[str] = None,
        provider: Optional[str] = None,
        openai_base_url: Optional[str] = None
    ):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_model = openai_model or os.getenv("ISPY_AI_MODEL", AI_DEFAULT_MODEL)
        self.gemini_model = gemini_model or os.getenv("ISPY_GEMINI_MODEL", "gemini-1.5-flash")
        self.openai_base_url = openai_base_url or os.getenv("ISPY_OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        self.provider = (provider or os.getenv("ISPY_AI_PROVIDER", "")).lower()
        if not self.provider:
            if self.gemini_api_key:
                self.provider = "gemini"
            elif self.openai_api_key:
                self.provider = "openai"
        self._openai_client = None
        self._gemini_client = None
        self._gemini_uses_new_sdk = False

    @property
    def openai_client(self):
        """Lazy-load OpenAI client"""
        if self._openai_client is None and self.openai_api_key:
            try:
                from openai import OpenAI
                if self.openai_base_url:
                    self._openai_client = OpenAI(
                        api_key=self.openai_api_key,
                        base_url=self.openai_base_url
                    )
                else:
                    self._openai_client = OpenAI(api_key=self.openai_api_key)
            except ImportError:
                pass
        return self._openai_client

    @property
    def gemini_client(self):
        """Lazy-load Gemini client"""
        if self._gemini_client is None and self.gemini_api_key:
            try:
                from google import genai as genai_client
                self._gemini_client = genai_client.Client(api_key=self.gemini_api_key)
                self._gemini_uses_new_sdk = True
            except ImportError:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.gemini_api_key)
                    self._gemini_client = genai.GenerativeModel(self.gemini_model)
                    self._gemini_uses_new_sdk = False
                except ImportError:
                    pass
        return self._gemini_client

    @property
    def is_available(self) -> bool:
        """Check if AI engine is available"""
        if self.provider == "gemini":
            return self.gemini_api_key is not None and self.gemini_client is not None
        return self.openai_api_key is not None and self.openai_client is not None

    def _generate_text(self, system: str, user: str, max_tokens: int, temperature: float) -> str:
        if self.provider == "gemini":
            client = self.gemini_client
            if not client:
                raise RuntimeError("Gemini client not available")
            prompt = f"{system}\n\n{user}".strip()
            model_candidates = [self.gemini_model]
            if self.gemini_model == "gemini-1.5-flash":
                model_candidates.append("gemini-1.5-flash-latest")
            if self.gemini_model == "gemini-1.5-pro":
                model_candidates.append("gemini-1.5-pro-latest")

            last_error = None
            for model_name in model_candidates:
                try:
                    if self._gemini_uses_new_sdk:
                        try:
                            from google.genai import types
                            config = types.GenerateContentConfig(
                                temperature=temperature,
                                max_output_tokens=max_tokens,
                            )
                            response = client.models.generate_content(
                                model=model_name,
                                contents=prompt,
                                config=config
                            )
                        except Exception:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=prompt
                            )
                        return response.text or ""
                    response = client.generate_content(
                        prompt,
                        generation_config={
                            "temperature": temperature,
                            "max_output_tokens": max_tokens,
                        },
                    )
                    return response.text or ""
                except Exception as exc:
                    last_error = exc
                    continue
            raise RuntimeError(str(last_error) if last_error else "Gemini generation failed")

        client = self.openai_client
        if not client:
            raise RuntimeError("OpenAI client not available")
        response = client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content or ""

    def analyze_logs(self, logs: str, context: str = "") -> AIAnalysisResult:
        """AI-powered log analysis"""
        if not self.is_available:
            return AIAnalysisResult(
                success=False,
                summary="",
                severity="Unknown",
                issues=[],
                recommendations=[],
                root_causes=[],
                error="AI key not configured. Set OPENAI_API_KEY or GEMINI_API_KEY."
            )

        try:
            # Truncate logs to avoid token limits
            truncated_logs = logs[:AI_MAX_LOG_CHARS]
            if len(logs) > AI_MAX_LOG_CHARS:
                truncated_logs += f"\n... [truncated, {len(logs) - AI_MAX_LOG_CHARS} more chars]"

            prompt = f"""Analyze the following iOS device logs and provide a structured assessment.

Context: {context or "General device diagnostic"}

Logs:
{truncated_logs}

Provide your analysis in the following JSON format:
{{
    "summary": "Brief summary of findings",
    "severity": "Low|Medium|High|Critical",
    "issues": ["List of identified issues"],
    "recommendations": ["List of actionable recommendations"],
    "root_causes": ["List of potential root causes"]
}}

Only respond with valid JSON."""

            content = self._generate_text(
                "You are an iOS diagnostics expert. Analyze device logs and provide actionable insights.",
                prompt,
                max_tokens=AI_MAX_TOKENS,
                temperature=0.3
            )

            # Parse JSON response
            try:
                # Handle markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                data = json.loads(content.strip())

                return AIAnalysisResult(
                    success=True,
                    summary=data.get("summary", ""),
                    severity=data.get("severity", "Unknown"),
                    issues=data.get("issues", []),
                    recommendations=data.get("recommendations", []),
                    root_causes=data.get("root_causes", []),
                    raw_response=content
                )
            except json.JSONDecodeError:
                return AIAnalysisResult(
                    success=True,
                    summary=content[:200],
                    severity="Unknown",
                    issues=[],
                    recommendations=[],
                    root_causes=[],
                    raw_response=content,
                    error="AI response was not valid JSON"
                )

        except Exception as e:
            return AIAnalysisResult(
                success=False,
                summary="",
                severity="Unknown",
                issues=[],
                recommendations=[],
                root_causes=[],
                error=f"AI analysis failed: {str(e)}"
            )

    def ask(self, question: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Answer a user question with optional structured context"""
        if not self.is_available:
            return None

        context_text = ""
        if context:
            try:
                context_text = json.dumps(context, indent=2, default=str)
            except TypeError:
                context_text = str(context)

        if len(context_text) > AI_MAX_CONTEXT_CHARS:
            context_text = context_text[:AI_MAX_CONTEXT_CHARS] + "\n... [truncated]"

        prompt = question
        if context_text:
            prompt = f"{question}\n\nContext:\n{context_text}"

        try:
            return self._generate_text(
                "You are an iOS forensics assistant. Use the provided context to answer clearly and precisely.",
                prompt,
                max_tokens=700,
                temperature=0.3
            )
        except Exception as e:
            return f"AI request failed: {str(e)}"

    def suggest_solution(self, problem: str, device: DeviceInfo) -> str:
        """Get AI-powered solution suggestions for a problem"""
        if not self.is_available:
            return "AI suggestions unavailable. Set OPENAI_API_KEY or GEMINI_API_KEY to enable."

        try:
            prompt = f"""As an iOS troubleshooting expert, help solve this problem:

Device Information:
- Model: {device.model}
- iOS Version: {device.version}
- Device Name: {device.name}

Problem Description:
{problem}

Provide clear, step-by-step troubleshooting instructions. Be specific and actionable.
If the problem might require Apple support, mention that as well."""

            return self._generate_text(
                "You are an expert iOS support technician with deep knowledge of Apple devices.",
                prompt,
                max_tokens=600,
                temperature=0.5
            ) or "No suggestions available."

        except Exception as e:
            return f"AI suggestion failed: {str(e)}"

    def analyze_diagnostics(self, diagnostics: Dict[str, Any], device: DeviceInfo) -> str:
        """Analyze full diagnostic results and provide summary"""
        if not self.is_available:
            return "AI analysis unavailable."

        try:
            # Summarize diagnostics for AI
            summary_parts = []
            for module, results in diagnostics.items():
                if "error" in results:
                    summary_parts.append(f"{module}: Error - {results['error']}")
                else:
                    key_metrics = {k: v for k, v in results.items()
                                   if k not in ["recommendations"] and not isinstance(v, list)}
                    summary_parts.append(f"{module}: {key_metrics}")

            diagnostics_text = "\n".join(summary_parts)

            prompt = f"""Analyze this iOS device diagnostic report and provide insights:

Device: {device.model} running iOS {device.version}

Diagnostic Results:
{diagnostics_text}

Provide:
1. Overall device health assessment (1-2 sentences)
2. Top 3 concerns (if any)
3. Top 3 recommendations for improvement

Keep the response concise and actionable."""

            return self._generate_text(
                "You are an iOS diagnostics expert providing concise device health assessments.",
                prompt,
                max_tokens=400,
                temperature=0.3
            ) or "Analysis complete."

        except Exception as e:
            return f"AI analysis failed: {str(e)}"

    def explain_error(self, error_message: str, context: str = "") -> str:
        """Explain an iOS error message in plain language"""
        if not self.is_available:
            return "AI unavailable for error explanation."

        try:
            prompt = f"""Explain this iOS error in simple terms and suggest how to fix it:

Error: {error_message}
Context: {context or "General iOS device error"}

Provide:
1. What this error means (1-2 sentences)
2. Most likely cause
3. Steps to fix it"""

            return self._generate_text(
                "You are an expert iOS support technician.",
                prompt,
                max_tokens=300,
                temperature=0.3
            ) or "Unable to explain error."

        except Exception as e:
            return f"Error explanation failed: {str(e)}"
