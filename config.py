"""Project configuration and environment validation."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # GCP
    google_cloud_project: str = Field("local-dev", description="GCP project ID")
    google_cloud_location: str = Field("us-central1", description="GCP region")
    google_application_credentials: str | None = Field(
        None, description="Path to service account key (optional)"
    )

    # Models
    router_model: str = "gemini-2.0-flash"
    idp_assistant_model: str = "gemini-2.0-flash"
    workflow_model: str = "gemini-2.0-flash"
    pipeline_model: str = "gemini-2.0-flash"
    approval_model: str = "gemini-2.0-flash"
    audit_model: str = "gemini-2.0-flash"
    execution_model: str = "gemini-2.0-flash"

    # Retrieval backend
    retrieval_backend: Literal["vertex-ai-search", "mock"] = "mock"
    vertex_ai_search_engine: str | None = None
    vertex_ai_search_location: str = "us-central1"

    # Harness IDP
    harness_idp_base_url: str = "https://app.harness.io/ng"
    harness_account_identifier: str | None = None
    harness_org_identifier: str = "default"
    harness_project_identifier: str | None = None
    harness_api_key_secret: str | None = None
    harness_delegate_selector: str = "act-delegate-k8s-ephub-p2r1"

    # Governance
    phi_redaction_enabled: bool = True
    audit_logging_enabled: bool = True
    secrets_via_vault: bool = True
    vault_addr: str | None = None

    # Observability
    log_level: str = "INFO"
    enable_cloud_logging: bool = True
    enable_cloud_trace: bool = True

    @field_validator("retrieval_backend")
    @classmethod
    def validate_retrieval_backend(cls, v: str) -> str:
        allowed = {"vertex-ai-search", "mock"}
        if v not in allowed:
            raise ValueError(f"retrieval_backend must be one of {allowed}")
        return v

    @field_validator("google_cloud_project", "harness_project_identifier")
    @classmethod
    def validate_required(cls, v: str | None, info) -> str | None:
        if v in (None, "", "your-gcp-project-id", "your-project"):
            return None
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
