"""Identity and secret access."""

from __future__ import annotations

from functools import lru_cache

from google.cloud import secretmanager

from config import Settings, get_settings


@lru_cache
def _secret_client() -> secretmanager.SecretManagerServiceClient:
    return secretmanager.SecretManagerServiceClient()


def get_harness_api_key(settings: Settings | None = None) -> str:
    """Return the Harness API key from Vault or Secret Manager."""
    settings = settings or get_settings()
    if settings.secrets_via_vault and settings.vault_addr:
        return _get_secret_from_vault("harness-api-key")
    if settings.harness_api_key_secret:
        return _get_secret_from_sm(settings.harness_api_key_secret)
    raise RuntimeError("No secret backend configured for Harness API key")


def _get_secret_from_vault(path: str) -> str:
    # Placeholder for Vault integration. Implement with hvac in production.
    raise NotImplementedError("Vault integration not implemented")


def _get_secret_from_sm(secret_version_resource: str) -> str:
    client = _secret_client()
    response = client.access_secret_version(request={"name": secret_version_resource})
    return response.payload.data.decode("utf-8")


def mask_secret(value: str, visible: int = 4) -> str:
    """Return a masked representation of a secret for logs."""
    if not value:
        return ""
    if len(value) <= visible:
        return "*" * len(value)
    return value[:visible] + "*" * (len(value) - visible)
