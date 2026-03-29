from pydantic import BaseModel, ConfigDict
from typing import Dict, Any

class AgentPayload(BaseModel):
    # This is exactly what a LangChain/CrewAI agent sends us over the wire
    tool_name: str
    arguments: Dict[str, Any]

        # Just tossing in an example so the docs look nice when the mentors test it
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tool_name": "fetch_incident_report",
                "arguments": {
                    "source_ip": "192.168.1.15",
                    "user_query": {"email": "attacker@darkweb.com", "notes": "Investigate immediately"},
                    "tags": ["urgent", "compromised_admin"]
                }
            }
        }
    )

class SanitizedPayload(BaseModel):
    # The clean version we actually let the agent look at
    processing_time_ms: float
    original_tool: str
    intercepted_entities: int
    sanitized_arguments: Dict[str, Any]
