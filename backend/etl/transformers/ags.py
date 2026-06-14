"""AGS normalization helpers."""
def normalize(value: object, width: int) -> str:
    """Normalize numeric-like values to a zero-padded AGS string."""
    return str(value).split(".")[0].strip().zfill(width)
def municipality_ags(state: object, regbez: object, district: object, municipality: object) -> str:
    """Build an eight-digit municipality AGS."""
    return normalize(state, 2) + normalize(regbez, 1) + normalize(district, 2) + normalize(municipality, 3)
def district_ags(state: object, regbez: object, district: object) -> str:
    """Build a five-digit district AGS."""
    return normalize(state, 2) + normalize(regbez, 1) + normalize(district, 2)
