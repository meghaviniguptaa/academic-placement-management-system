def is_positive_int(value):
    """Check whether a value is a positive integer."""
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value > 0
    )


def get_missing_fields(data, required_fields):
    """Return required fields that are missing or empty."""
    if not isinstance(data, dict):
        return list(required_fields)

    return [
        field
        for field in required_fields
        if data.get(field) is None
        or (
            isinstance(data.get(field), str)
            and not data[field].strip()
        )
    ]
