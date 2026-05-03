import json

from tunafactory.data.diagnose import diagnose_dataset


def test_diagnose_dataset_outputs_report_and_annotations(tmp_path):
    input_file = tmp_path / "dataset.jsonl"
    rows = [
        {"id": "1", "messages": [{"role": "user", "content": "What is tuna?"}, {"role": "assistant", "content": "ok"}]},
        {"id": "2", "messages": [{"role": "user", "content": "What is tuna?"}, {"role": "assistant", "content": "A fish"}]},
        {"id": "3", "messages": [{"role": "user", "content": "What is tuna??"}, {"role": "assistant", "content": "A fish"}]},
    ]
    input_file.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    out_dir = tmp_path / "tunafactory_output"
    _, result = diagnose_dataset(str(input_file), output_dir=str(out_dir))

    assert "Issues found" in result["report"]
    assert (out_dir / "report.txt").exists()
    assert (out_dir / "annotated.jsonl").exists()

    annotations = [json.loads(line) for line in (out_dir / "annotated.jsonl").read_text().splitlines()]
    by_id = {item["id"]: item["issues"] for item in annotations}

    assert "low_quality" in by_id["1"]
    assert "contradiction" in by_id["1"]
    assert "duplicate" in by_id["2"]
    assert "duplicate" in by_id["3"]
