import json
from pathlib import Path


def save_errors(errors, output_dir):

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_dir / "errors.json"

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            errors,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"errors.json saved → {output_file}"
    )
