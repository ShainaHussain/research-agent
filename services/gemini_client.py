"""
gemini_client.py
------------------
Drop-in replacement for claude_client.py, using Google's Gemini API
(genuinely free tier, no credit card needed).

Uses the current `google-genai` SDK (the old `google-generativeai`
package was deprecated by Google in late 2025).

Get a free key at: https://aistudio.google.com/apikey

Same two functions as claude_client.py: analyze_papers() and synthesize_gaps()
so you can swap the import in app.py with zero other changes:

    from claude_client import analyze_papers, synthesize_gaps
    -->
    from gemini_client import analyze_papers, synthesize_gaps
"""

import os
import json
import re
from google import genai

MODEL = "gemini-3.6-flash"  # current model, free tier friendly


def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Get a free key at "
            "https://aistudio.google.com/apikey and add it to .env"
        )
    return genai.Client(api_key=api_key)


def _extract_json(text: str):
    cleaned = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(cleaned.strip())


def analyze_papers(papers: list[dict], experience_level: str = "beginner") -> list[dict]:
    client = _get_client()

    paper_blocks = ""
    for i, p in enumerate(papers):
        paper_blocks += f"\n\n[PAPER {i}]\nTitle: {p['title']}\nAbstract: {p['summary']}"

    prompt = f"""You are a research assistant helping a {experience_level} researcher
review academic papers. For EACH paper below, extract the following fields.
Write in plain, simple language a {experience_level} could understand.

For each paper return:
- "index": the paper number (matching [PAPER N])
- "plain_summary": 2-3 sentences, what the paper actually does, in simple terms
- "method": the core method/approach used (short phrase)
- "future_work": what the paper explicitly says is future work / not yet done (or "Not explicitly stated" if none)
- "gap": your own inference of a limitation or gap in this paper, even if not explicitly stated
- "difficulty": one of "Beginner", "Intermediate", "Advanced" — how hard this paper is to read

Papers:
{paper_blocks}

Return ONLY a JSON array, one object per paper, no preamble, no markdown fences, no explanation.
Example shape:
[{{"index": 0, "plain_summary": "...", "method": "...", "future_work": "...", "gap": "...", "difficulty": "Beginner"}}]
"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    analyses = _extract_json(response.text)

    for a in analyses:
        idx = a["index"]
        papers[idx].update({
            "plain_summary": a.get("plain_summary", ""),
            "method": a.get("method", ""),
            "future_work": a.get("future_work", ""),
            "gap": a.get("gap", ""),
            "difficulty": a.get("difficulty", "Intermediate"),
        })

    return papers


def synthesize_gaps(papers: list[dict], topic: str) -> dict:
    client = _get_client()

    summary_blocks = ""
    for i, p in enumerate(papers):
        summary_blocks += (
            f"\n\nPaper {i}: {p['title']}\n"
            f"Summary: {p.get('plain_summary', '')}\n"
            f"Method: {p.get('method', '')}\n"
            f"Stated future work: {p.get('future_work', '')}\n"
            f"Inferred gap: {p.get('gap', '')}"
        )

    prompt = f"""You are a research mentor helping a beginner researcher find a
novel research direction in the topic: "{topic}"

Here is what they've read so far:
{summary_blocks}

Do the following:
1. Identify 2-4 CROSS-CUTTING gaps — patterns that show up when you look at
   ALL these papers TOGETHER (e.g. "most papers focus on X, almost none address Y").
2. For each gap, briefly explain WHY it matters and WHICH papers support this observation.
3. Suggest 2-3 concrete, specific research questions the user could pursue,
   each tied to one of the gaps above, with a one-line rationale for why it's
   feasible and not already well-covered.

Return ONLY valid JSON in this shape, no markdown fences, no preamble:
{{
  "cross_cutting_gaps": [
    {{"gap": "...", "why_it_matters": "...", "supporting_papers": ["Paper 0", "Paper 2"]}}
  ],
  "suggested_questions": [
    {{"question": "...", "rationale": "..."}}
  ]
}}
"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return _extract_json(response.text)