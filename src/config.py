from pydantic import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    hook_secret_token: Optional[str] = None
    ci_workflow_name: str = "testing"
    host: str = "127.0.0.1"
    port: int = 8000
    base_dir: Path = Path("~/localdeploy/managed")

settings = Settings()
settings.base_dir.mkdir(exist_ok=True)
