"""HashiCorp Vault secret store adapter."""

from __future__ import annotations

from .base import SecretStore


class VaultSecretStore(SecretStore):
    """Production adapter for HashiCorp Vault KV secrets."""

    def __init__(self, addr: str | None = None, token: str | None = None) -> None:
        self._addr = addr
        self._token = token

    def get_secret(self, name: str) -> str:
        # Placeholder: implement with hvac in production.
        raise NotImplementedError(
            "Vault integration is not implemented. Install hvac and configure VAULT_ADDR."
        )
