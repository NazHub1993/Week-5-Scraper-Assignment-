def normalize_price(price_text):

    if not price_text:
        return None

    price = (
        price_text
        .replace("£", "")
        .replace("Â", "")
        .strip()
    )

    return float(price)


def normalize_book(record):

    normalized_record = record.copy()

    normalized_record["price_gbp"] = normalize_price(
        record["price_text"]
    )

    return normalized_record
