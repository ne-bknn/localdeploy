import uvicorn
from src import settings

if __name__ == "__main__":
    uvicorn.run("src:app", host=settings.host, port=settings.port, log_level="info")
