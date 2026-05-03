from __future__ import annotations

import argparse
import json

from tunafactory.data.diagnose import diagnose_dataset
from tunafactory.data.prepare import prepare_dataset
from tunafactory.eval.report import build_report
from tunafactory.export.service import export_run
from tunafactory.run.launch import launch_finetune


def main() -> None:
    parser = argparse.ArgumentParser(prog="tunafactory")
    sub = parser.add_subparsers(dest="command", required=True)

    data = sub.add_parser("data")
    data_sub = data.add_subparsers(dest="data_cmd", required=True)
    prepare = data_sub.add_parser("prepare")
    diagnose = data_sub.add_parser("diagnose")
    diagnose.add_argument("input_path")
    prepare.add_argument("input_path")
    prepare.add_argument("--output-dir", default="prepared_dataset")
    prepare.add_argument("--format", dest="fmt", default=None)

    run = sub.add_parser("run")
    run_sub = run.add_subparsers(dest="run_cmd", required=True)
    finetune = run_sub.add_parser("finetune")
    finetune.add_argument("--model", required=True)
    finetune.add_argument("--dataset", required=True)
    finetune.add_argument("--preset", default="small")

    ev = sub.add_parser("eval")
    ev_sub = ev.add_subparsers(dest="eval_cmd", required=True)
    report = ev_sub.add_parser("report")
    report.add_argument("--run", required=True)

    ex = sub.add_parser("export")
    ex.add_argument("--run", required=True)
    ex.add_argument("--target", required=True)

    args = parser.parse_args()

    if args.command == "data" and args.data_cmd == "prepare":
        _, summary = prepare_dataset(args.input_path, args.output_dir, fmt=args.fmt)
        print(json.dumps(summary, indent=2))
    elif args.command == "data" and args.data_cmd == "diagnose":
        _, result = diagnose_dataset(args.input_path)
        print(result["report"])
    elif args.command == "run" and args.run_cmd == "finetune":
        run_dir = launch_finetune(args.model, args.dataset, preset=args.preset)
        print(run_dir)
    elif args.command == "eval" and args.eval_cmd == "report":
        report_path = build_report(args.run)
        print(report_path)
    elif args.command == "export":
        export_path = export_run(args.run, args.target)
        print(export_path)


if __name__ == "__main__":
    main()
