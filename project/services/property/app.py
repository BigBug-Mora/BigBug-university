from fastapi import FastAPI

app = FastAPI(title="EstateFlow Property Service")


@app.get("/health")
async def health() -> dict[str, str]:
    """Report that the Property API is running."""
    return {"status": "ok"}
