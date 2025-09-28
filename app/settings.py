from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    notion_api_token: str = ""
    notion_rel_project_to_notes: str = "Notes"
    notion_rel_project_to_tasks: str = "Tasks"
    notion_project_pdf_url_prop: str = "Latest PDF URL"
    gcs_bucket: str = ""
    local_storage_path: str = "./local_reports"
    use_local_storage: bool = True
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


settings = Settings()
