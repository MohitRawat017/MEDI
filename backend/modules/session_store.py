# Simple in-memory store (per server instance)

SESSION_STORE = {}


def save_session(session_id: str, prescription_json: dict):
    SESSION_STORE[session_id] = prescription_json


def get_session(session_id: str):
    return SESSION_STORE.get(session_id)
