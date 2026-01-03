def keys_to_int(x):
    return {int(k) if k.isdigit() else k: v for k, v in x.items()}

def strip_formatting(string: str) -> str:
    return string.replace("\n", "").replace("\t", "").replace("\r", "")
