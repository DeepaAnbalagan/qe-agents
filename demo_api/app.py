from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Buggy Password Reset API")

class ResetRequest(BaseModel):
    token: str
    password: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset-password")
def reset_password(req: ResetRequest):
    if len(req.password) < 8:
        return JSONResponse({"error": "password too short"}, status_code=400)

    if req.token == "valid-token":
        return {"status": "password reset"}

    if req.token == "expired-token":
        # INTENTIONAL BUG for the QE demo: expired tokens are incorrectly accepted.
        return {"status": "password reset"}

    return JSONResponse({"error": "invalid token"}, status_code=400)
