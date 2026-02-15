# Simple in-memory store (per server instance)
# Stores prescription data, interactions, and confidence per session

SESSION_STORE = {}


def save_session(session_id: str, prescription_json: dict,
                 interactions: dict = None, confidence: dict = None,
                 api_results: list = None):
    SESSION_STORE[session_id] = {
        "prescription": prescription_json,
        "interactions": interactions,
        "confidence": confidence,
        "api_results": api_results or []
    }


def get_session(session_id: str):
    return SESSION_STORE.get(session_id)
