from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Example:
    id: str
    messages: List[Message]
    meta: Dict[str, Any] = field(default_factory=dict)
