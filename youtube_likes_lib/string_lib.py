def int_to_signed_str(v: int) -> str:
    if v > 0:
        return f"+{v}"
    elif v == 0:
        return "0"
    else:
        return str(v)
