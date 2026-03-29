from fastapi import FastAPI, HTTPException
from models import AgentPayload, SanitizedPayload
from engine import traverse_ast_and_sanitize
import time

app = FastAPI(
    title="PII-Safe Middleware MVP",
    description="GSoC 2026 Proof of Concept: High-Speed AST JSON Payload Sanitization.",
    version="0.1.0"
)

@app.post("/api/v1/sanitize", response_model=SanitizedPayload)
async def sanitize_payload(payload: AgentPayload):
    # Hit the timer so we can prove this is actually fast
    start_time = time.perf_counter()
    
    try:
        # Pass the raw arguments payload to our AST traverse engine
        sanitized_args, entity_count = traverse_ast_and_sanitize(payload.arguments)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return SanitizedPayload(
            processing_time_ms=round(elapsed_ms, 3), # Keep to 3 decimals to show off the sub-2ms speed
            original_tool=payload.tool_name,
            sanitized_arguments=sanitized_args,
            intercepted_entities=entity_count
        )
    except Exception as e:
        # Failsafe: if the parser crashes, we throw a 500 error instead of leaking data
        raise HTTPException(status_code=500, detail=str(e))
