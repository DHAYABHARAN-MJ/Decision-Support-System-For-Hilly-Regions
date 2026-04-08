# dss/validators.py  v3 — real numeric inputs for elevation, moisture, building_load

FIELD_RULES = {
    "slope_angle":      (float, 0, 90),
    "elevation":        (float, 0, 5000),          # metres AMSL
    "landslide_risk":   (str,   ["low", "medium", "high"]),
    "soil_type":        (str,   ["rock", "clay", "sandy"]),
    "bearing_capacity": (float, 0, 2000),           # kN/m2
    "moisture_content": (float, 0, 100),            # percentage %
    "num_floors":       (int,   1, 50),
    "foundation_type":  (str,   ["pile","raft","stepped","shallow","isolated","combined","under_reamed"]),
    "building_load":    (float, 0, 100),            # kN/m2 total floor load
    "material":         (str,   ["concrete", "steel", "wood"]),
    "wall_type":        (str,   ["reinforced", "brick", "lightweight"]),
    "retaining_wall":   (str,   ["yes", "no"]),
    "drainage":         (str,   ["yes", "no"]),
    "seismic_zone":     (int,   1, 5),
    "usage":            (str,   ["residential", "commercial"]),
}


def validate_params(data: dict) -> tuple:
    errors = {}
    cleaned = {}
    for field, rules in FIELD_RULES.items():
        if field not in data:
            errors[field] = f"'{field}' is required."
            continue
        val = data[field]
        dtype = rules[0]
        constraints = rules[1:]
        try:
            if dtype == float:
                val = float(val)
            elif dtype == int:
                val = int(float(val))
            elif dtype == str:
                val = str(val).lower().strip()
        except (ValueError, TypeError):
            errors[field] = f"'{field}' must be {dtype.__name__}."
            continue
        if dtype in (float, int):
            mn, mx = constraints
            if not (mn <= val <= mx):
                errors[field] = f"'{field}' must be between {mn} and {mx}. Got {val}."
                continue
        if dtype == str:
            allowed = constraints[0]
            if val not in allowed:
                errors[field] = f"'{field}' must be one of {allowed}. Got '{val}'."
                continue
        cleaned[field] = val
    return cleaned, errors
