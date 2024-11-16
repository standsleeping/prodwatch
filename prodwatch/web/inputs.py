import json
from starlette.requests import Request


async def parse_json_request(request: Request) -> dict | None:
    """Attempts to parse JSON from request body. Returns None if parsing fails."""
    try:
        return await request.json()
    except json.JSONDecodeError:
        return None