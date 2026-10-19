
import logging
import os
import secrets
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import generate, study_plan


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("quizcraftqa-ai")

app = FastAPI(
    title="QuizCraftQA AI Backend",
    description="Gemini-powered question generation for QuizCraftQA",
    version="1.0.0",
)

# Comma-separated list of browser origins allowed to call the API.
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "https://sudarshanchaudhari.github.io,http://localhost:5173"
).split(",")


def require_api_token(x_api_token: str = Header(default="")):
    # CORS does not stop non-browser clients, so every Gemini-backed route needs the shared token.
    expected = os.getenv("API_TOKEN", "")
    if not expected or not secrets.compare_digest(x_api_token.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Unauthorized")


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} {request.method} {request.url}")
    return response

app.include_router(generate.router, dependencies=[Depends(require_api_token)])
app.include_router(study_plan.router, dependencies=[Depends(require_api_token)])



@app.get("/")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok", "service": "QuizCraftQA-AI"}
