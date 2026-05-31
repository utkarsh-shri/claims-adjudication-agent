from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from api import claims, review, dashboard

app = FastAPI(title="Claims Adjudication API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims.router, prefix="/api/claims", tags=["claims"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Claims Adjudication API is running"}
