"""Start the EstateFlow Property service for local development."""

import sys
from pathlib import Path

import uvicorn


if __name__ == "__main__":
    if __package__ is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    uvicorn.run(
        "project.services.property.app:create_app", factory=True, host="127.0.0.1", port=8000
    )
