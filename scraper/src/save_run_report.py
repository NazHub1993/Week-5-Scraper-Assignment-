from pathlib import Path
import json



def save_run_report(report, output_dir):

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_dir / "run-report.json"

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"run-report.json saved: {output_file}"
    )



