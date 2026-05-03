from __future__ import annotations

from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, Iterable, List


GENERIC_LOW_QUALITY = {
    "ok",
    "okay",
    "yes",
    "no",
    "i don't know",
    "idk",
    "n/a",
}


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _last_message(messages: list[dict], role: str) -> str:
    for message in reversed(messages):
        if message.get("role") == role:
            return str(message.get("content", ""))
    return ""


def detect_duplicates(rows: Iterable[dict], similarity_threshold: float = 0.92) -> Dict[str, object]:
    rows = list(rows)
    signatures = defaultdict(list)
    examples = []

    for index, row in enumerate(rows):
        prompt = _normalize(_last_message(row.get("messages", []), "user"))
        answer = _normalize(_last_message(row.get("messages", []), "assistant"))
        signatures[f"{prompt}|||{answer}"].append(index)

    duplicate_indexes = set()
    for indexes in signatures.values():
        if len(indexes) > 1:
            duplicate_indexes.update(indexes)

    prompts = [
        _normalize(_last_message(row.get("messages", []), "user"))
        for row in rows
    ]
    for i in range(len(prompts)):
        if not prompts[i]:
            continue
        for j in range(i + 1, len(prompts)):
            if j in duplicate_indexes:
                continue
            ratio = SequenceMatcher(None, prompts[i], prompts[j]).ratio()
            if ratio >= similarity_threshold:
                duplicate_indexes.update((i, j))

    if duplicate_indexes:
        examples = [rows[i].get("id", f"row_{i}") for i in sorted(duplicate_indexes)[:5]]

    return {
        "indexes": duplicate_indexes,
        "count": len(duplicate_indexes),
        "ratio": (len(duplicate_indexes) / len(rows)) if rows else 0.0,
        "examples": examples,
    }


def detect_contradictions(rows: Iterable[dict]) -> Dict[str, object]:
    rows = list(rows)
    by_prompt = defaultdict(set)
    prompt_to_indexes = defaultdict(list)

    for i, row in enumerate(rows):
        prompt = _normalize(_last_message(row.get("messages", []), "user"))
        answer = _normalize(_last_message(row.get("messages", []), "assistant"))
        if prompt and answer:
            by_prompt[prompt].add(answer)
            prompt_to_indexes[prompt].append(i)

    contradictory_indexes = set()
    contradictory_prompts = 0
    for prompt, answers in by_prompt.items():
        if len(answers) > 1:
            contradictory_prompts += 1
            contradictory_indexes.update(prompt_to_indexes[prompt])

    return {
        "indexes": contradictory_indexes,
        "count": contradictory_prompts,
        "samples": len(contradictory_indexes),
    }


def detect_low_quality(rows: Iterable[dict], short_words: int = 3) -> Dict[str, object]:
    rows = list(rows)
    indexes = set()
    for i, row in enumerate(rows):
        answer = _normalize(_last_message(row.get("messages", []), "assistant"))
        words = [w for w in answer.split(" ") if w]
        if answer in GENERIC_LOW_QUALITY or len(words) <= short_words:
            indexes.add(i)

    return {
        "indexes": indexes,
        "count": len(indexes),
        "ratio": (len(indexes) / len(rows)) if rows else 0.0,
    }
