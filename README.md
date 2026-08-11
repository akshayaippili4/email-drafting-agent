# Email Drafting Agent

A LangChain-based workflow that drafts professional emails. The app first analyzes the request and then generates the final email with a second prompt.

**Framework**: LangChain  
**LLM**: Ollama `gpt-oss:120b-cloud`  
**UI**: Flask + HTML/CSS  

## Setup

```bash
pip install -r requirements.txt
```

Make sure [Ollama](https://ollama.com) is running and the model is available:

```bash
ollama pull gpt-oss:120b-cloud
```

## Run (Web UI)

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Run (CLI)

```bash
# Default example
python agent.py

# Custom email
python agent.py \
  --context "Apologize for the delayed delivery of the software project" \
  --tone "apologetic but confident" \
  --recipient "the client project manager"
```

## Architecture

```
Context → [Analysis Prompt] → Brief → [Draft Prompt] → Final Email
```
