import re

def extract_consumer_number(text):

    clean = text.replace("\n", " ")

    match = re.search(r"ग्राहक\s*क्रमांक[:\s]*([0-9]{12})", clean)
    if match:
        return match.group(1)

    matches = re.findall(r":\s*([0-9]{12})", clean)
    for m in matches:
        if not m.startswith(("201", "202")):
            return m

    nums = re.findall(r"\b[0-9]{12}\b", clean)
    for n in nums:
        if not n.startswith(("201", "202")):
            return n

    return None