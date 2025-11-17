from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Marzban Proxy for Mini App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from config import MARZBAN_CONFIG

MARZBAN_URL = MARZBAN_CONFIG["host"].rstrip("/")
MARZBAN_TOKEN_FILE = MARZBAN_CONFIG.get("token_file", "marzban_token.txt")

with open(MARZBAN_TOKEN_FILE, "r") as f:
    MARZBAN_TOKEN = f.read().strip()

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    url = f"{MARZBAN_URL}/api/{path}"

    headers = {
        "Authorization": f"Bearer {MARZBAN_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )

        if "text/plain" in response.headers.get("content-type", ""):
            return StreamingResponse(response.aiter_bytes(), media_type="text/plain")

        try:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception:
            return JSONResponse(
                content={"detail": "Invalid JSON from Marzban"},
                status_code=500
            )
