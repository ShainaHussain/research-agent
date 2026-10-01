# Research Partner — Core Prototype

This is the bare-bones proof-of-concept: **topic → arXiv papers → Claude-generated
plain-language summaries → gap table → cross-paper gap synthesis → suggested
research questions.**

No auth, no database, no teams yet — just the core loop, to prove the idea works.

## What it does

1. You type a research topic (e.g. "Federated Learning in IoT")
2. It fetches real papers from arXiv (free API, no key needed)
3. Claude reads each abstract and extracts: plain summary, method, stated
   future work, an inferred gap, and a difficulty rating
4. Everything is shown in a sortable table
5. Click "Generate Cross-Paper Gap Synthesis" and Claude looks across ALL the
   papers together to find patterns — gaps that only show up when you compare
   papers, plus 2-3 concrete research question suggestions
6. Export the table as CSV

## Setup (5 minutes)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Claude API key
- Go to https://console.anthropic.com/
- Create an API key

### 3. Add your key
```bash
cp .env.example .env
```
Open `.env` and paste your key:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### 4. Run it
```bash
streamlit run app.py
```
This opens the app in your browser, usually at `http://localhost:8501`

## File structure

```
research_partner/
├── app.py              # Streamlit UI — the main entry point
├── arxiv_client.py      # Fetches papers from arXiv (free, no key needed)
├── claude_client.py      # Calls Claude API for analysis + gap synthesis
├── requirements.txt     # Python dependencies
├── .env.example          # Template for your API key
└── README.md
```

## How the Claude calls work (for your report/presentation)

- **Per-paper analysis** (`analyze_papers` in `claude_client.py`): all paper
  abstracts are sent in ONE batched call (not one call per paper) to keep it
  fast and cheap. Claude returns structured JSON per paper.
- **Cross-paper synthesis** (`synthesize_gaps`): takes all the per-paper
  summaries and asks Claude to find patterns ACROSS them — this is the
  differentiator from tools that only summarize one paper at a time.

## Known limitations (expected — this is a v1 prototype)

- Only searches arXiv (add Semantic Scholar / PubMed later for other fields)
- No saving between sessions — refresh and you lose your results
- No auth or multi-user support yet (see the architecture doc for that plan)
- Claude's "gap" field is an inference, not a guarantee — always sanity-check
  against the actual paper

## Next steps (once this works)

1. Add Semantic Scholar as a second paper source
2. Add a database (Postgres/Firebase) so results persist
3. Add user auth + the team collaboration features
4. Add the "Research Question Refinement" follow-up screen
5. Add the literature review draft generator

---
Built as the MVP core loop for the Research Partner project.
