# PII-Safe: GSoC 2026 Sandbox

Hey! If you're reading this, you are probably reviewing my GSoC 2026 proposal for **Project #12: PII-Safe (Privacy Guard for Agentic AI & MCP Workflows)**.

I built this rapid Proof of Concept (MVP) specifically to tangibly demonstrate the core architectural claim of my proposal: **Blind regex destroys LLM payloads; we need schema-aware AST parsing.**

> [!NOTE]
> **What this is (and what it isn't):**
> This repo is just a playground to prove that recursive AST JSON traversal is faster and safer than flattening payloads into corrupted strings. 
> 
> *It does not* include the massive components I'll be building during the actual 350-hour GSoC timeline (like the `Redis` stateful TokenVault, the `SQLAlchemy` distributed audit log, the `spaCy` NLP models, or the native `stdio/SSE` MCP Server implementation). For those, check the timeline in my proposal!

---

## Why I built this MVP

When researching how LangChain and CrewAI handle tool-calls, I noticed a huge problem. If an agent fetches a database record that looks like this:
`{"user": "admin", "metadata": {"email": "target@corp.com", "logs": [...]}}`

If we just run a standard regex replace over that entire string, we risk destroying the JSON syntax completely (e.g., breaking quotes or brackets), which makes the LLM hallucinate or crash because it can't parse the broken JSON back into a Python dictionary.

### **The Solution (Demonstrated here):**
I built a specific `traverse_ast_and_sanitize` engine.
1. It physically walks the JSON Abstract Syntax Tree (AST).
2. It completely ignores structural `keys` (so the schema never breaks).
3. It only runs the deep regex sweep on the actual leaf `values`.
4. It does all of this in **< 2 milliseconds** via a fast-path regex bypass.

---

## How to test it yourself

I wanted to make this extremely easy for the mentors to spin up and test without battling dependency hell. It's just vanilla FastAPI and Pydantic.

### 1. Boot the interceptor
```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### 2. Throw some nasty JSON at it
I've already hooked up a beautiful Swagger UI. Just head to:
👉 `http://127.0.0.1:8000/docs`

Or, just use this PowerShell-friendly command to see how the AST parser safely rips out the deep nested IPs and Emails without touching the rest of the dictionary:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/sanitize" -Method Post -Body '{"tool_name": "fetch_incident_report", "arguments": {"source_ip": "192.168.1.15", "user_query": {"email": "attacker@darkweb.com", "notes": "Investigate immediately"}, "tags": ["urgent"]}}' -ContentType "application/json"
```

Watch how fast the `processing_time_ms` is in the response. I've designed it to be totally transparent and non-blocking for agentic workflows.

Thanks for taking the time to review my proposal, and I'm really looking forward to (hopefully!) building the real enterprise version of this with you this summer.
