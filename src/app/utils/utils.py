import re
def filter_compliances(compliances, expression: str) -> list:
    """Filter compliances by include/exclude using ID or name (case-insensitive)."""
    expression = expression.lower()

    include_terms = set()
    exclude_terms = set()

    if "include" in expression:
        match = re.search(r"include\s*:\s*([^\n\r]*)", expression)
        if match:
            include_terms = set(map(str.strip, match.group(1).split(",")))

    if "exclude" in expression:
        match = re.search(r"exclude\s*:\s*([^\n\r]*)", expression)
        if match:
            exclude_terms = set(map(str.strip, match.group(1).split(",")))

    def match_term(comp, terms):
        return (
            comp.id.lower() in terms or
            comp.name.lower() in terms
        )

    result = []
    for comp in compliances:
        comp_id = comp.id.lower()
        comp_name = comp.name.lower()

        # if include is defined, must match at least one
        if include_terms and not match_term(comp, include_terms):
            continue
        # exclude takes precedence
        if exclude_terms and match_term(comp, exclude_terms):
            continue

        result.append(comp)

    return result
