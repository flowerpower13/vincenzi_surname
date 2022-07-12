pat=r"(?!exceptfor)[^\w\s]"
exc="-"
pat=pat.replace("exceptfor", exc)
print(pat)