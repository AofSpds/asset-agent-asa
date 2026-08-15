from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class ShadowState:
    events_applied: int = 0
    last_event_id: str | None = None
    objects: dict[str, Mapping[str, Any]] = field(default_factory=dict)


def reduce_events(events: Iterable[Mapping[str, Any]]) -> ShadowState:
    """Build a non-authoritative AAA shadow projection from immutable events."""
    objects: dict[str, Mapping[str, Any]] = {}
    seen: set[str] = set()
    last_event_id: str | None = None
    count = 0

    for event in events:
        event_id = str(event.get("event_id", ""))
        if not event_id:
            raise ValueError("event_id is required")
        if event_id in seen:
            raise RuntimeError(f"DUPLICATE_EVENT: {event_id}")
        seen.add(event_id)

        object_id = str(event.get("object", event_id))
        objects[object_id] = dict(event)
        last_event_id = event_id
        count += 1

    return ShadowState(events_applied=count, last_event_id=last_event_id, objects=objects)


def assert_idempotent_rebuild(events: list[Mapping[str, Any]]) -> None:
    first = reduce_events(events)
    second = reduce_events(events)
    if first != second:
        raise RuntimeError("NON_DETERMINISTIC_REBUILD")
