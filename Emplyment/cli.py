from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import EmploymentRequest
from .service import EmploymentAdvisor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal employment market analysis and guidance tool")
    parser.add_argument("query", nargs="?", help="Employment question to analyze")
    parser.add_argument(
        "--mode",
        choices=["auto", "market", "guidance"],
        default="auto",
        help="Analysis mode",
    )
    parser.add_argument(
        "--profile-json",
        default="",
        help="Inline JSON string for candidate profile",
    )
    parser.add_argument(
        "--profile-file",
        default="",
        help="Path to a JSON file containing candidate profile",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save the markdown report to disk",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print the report and suppress the trailing metadata output",
    )
    return parser.parse_args()


def load_profile(args: argparse.Namespace) -> dict[str, object]:
    if args.profile_json:
        return json.loads(args.profile_json)
    if args.profile_file:
        return json.loads(Path(args.profile_file).read_text(encoding="utf-8"))
    return {}


def main() -> None:
    args = parse_args()
    query = args.query or input("请输入就业分析问题: ").strip()
    if not query:
        raise SystemExit("query 不能为空")

    advisor = EmploymentAdvisor()
    report = advisor.analyze(
        EmploymentRequest(
            query=query,
            mode=args.mode,
            profile=load_profile(args),
            save=not args.no_save,
        )
    )

    print(report.markdown)
    if not args.print_only:
        print("\n---")
        print(f"mode: {report.mode}")
        print(f"used_llm: {report.used_llm}")
        print(f"used_search: {report.used_search}")
        print(f"search_results: {len(report.search_results)}")
        print(f"output_path: {report.output_path or 'not saved'}")


if __name__ == "__main__":
    main()
