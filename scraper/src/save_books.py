import json
from pathlib import Path


def save_books(records, output_dir):

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    books_data = [
        book.model_dump(mode="json")
        for book in records
    ]

    output_file = output_dir / "books.json"

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            books_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"books.json saved → {output_file}"
    )
