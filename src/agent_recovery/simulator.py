from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping


class SimulationError(RuntimeError):
    """Raised when a synthetic enterprise operation cannot be completed."""


@dataclass
class SyntheticEnterprise:
    """Small deterministic enterprise used for safe recovery benchmarks."""

    crm_contacts: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "c-1": {"name": "Alex Rivera", "tier": "standard", "owner": "team-a"},
        }
    )
    permissions: dict[str, set[str]] = field(
        default_factory=lambda: {"agent-1": {"crm:read", "crm:write"}}
    )
    config: dict[str, Any] = field(default_factory=lambda: {"deploy_mode": "safe"})
    messages: list[dict[str, Any]] = field(default_factory=list)
    memory: dict[str, str] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        return {
            "crm_contacts": deepcopy(self.crm_contacts),
            "permissions": {key: sorted(value) for key, value in self.permissions.items()},
            "config": deepcopy(self.config),
            "messages": deepcopy(self.messages),
            "memory": deepcopy(self.memory),
        }

    def update_contact(self, params: Mapping[str, object]) -> dict[str, Any]:
        contact_id = str(params["contact_id"])
        field_name = str(params["field"])
        value = params["value"]
        if contact_id not in self.crm_contacts:
            raise SimulationError("contact not found")
        before = deepcopy(self.crm_contacts[contact_id])
        self.crm_contacts[contact_id][field_name] = value
        return {"before": before, "after": deepcopy(self.crm_contacts[contact_id])}

    def restore_contact(self, params: Mapping[str, object]) -> dict[str, Any]:
        contact_id = str(params["contact_id"])
        previous = deepcopy(params["previous"])
        if not isinstance(previous, dict):
            raise SimulationError("previous contact state must be a mapping")
        self.crm_contacts[contact_id] = previous
        return {"after": deepcopy(self.crm_contacts[contact_id])}

    def get_contact(self, params: Mapping[str, object]) -> dict[str, Any]:
        contact_id = str(params["contact_id"])
        return deepcopy(self.crm_contacts[contact_id])

    def grant_permission(self, params: Mapping[str, object]) -> dict[str, Any]:
        principal = str(params["principal"])
        permission = str(params["permission"])
        before = sorted(self.permissions.setdefault(principal, set()))
        self.permissions[principal].add(permission)
        return {"before": before, "after": sorted(self.permissions[principal])}

    def revoke_permission(self, params: Mapping[str, object]) -> dict[str, Any]:
        principal = str(params["principal"])
        permission = str(params["permission"])
        self.permissions.setdefault(principal, set()).discard(permission)
        return {"after": sorted(self.permissions[principal])}

    def get_permissions(self, params: Mapping[str, object]) -> list[str]:
        principal = str(params["principal"])
        return sorted(self.permissions.setdefault(principal, set()))

    def send_message(self, params: Mapping[str, object]) -> dict[str, Any]:
        message = {
            "channel": str(params["channel"]),
            "body": str(params["body"]),
            "observed": bool(params.get("observed", True)),
        }
        self.messages.append(message)
        return {"message_index": len(self.messages) - 1, "message": deepcopy(message)}

    def get_message(self, params: Mapping[str, object]) -> dict[str, Any]:
        index = int(params["message_index"])
        return deepcopy(self.messages[index])

    def write_memory(self, params: Mapping[str, object]) -> dict[str, Any]:
        key = str(params["key"])
        before = self.memory.get(key)
        self.memory[key] = str(params["value"])
        return {"before": before, "after": self.memory[key]}

    def restore_memory(self, params: Mapping[str, object]) -> dict[str, Any]:
        key = str(params["key"])
        previous = params.get("previous")
        if previous is None:
            self.memory.pop(key, None)
        else:
            self.memory[key] = str(previous)
        return {"after": self.memory.get(key)}

    def get_memory(self, params: Mapping[str, object]) -> str | None:
        return self.memory.get(str(params["key"]))
