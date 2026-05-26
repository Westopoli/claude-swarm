"""Type contract for link_extractor.

Minimal symbols required to encode the spec's inputs, outputs, and main
behaviors as type signatures. Sentinel bodies only — actual behavior lives
in leaf impls downstream.
"""

# encodes spec.md "Inputs" (URL string) and "Outputs" (the links found)
# encodes spec.md acceptance criteria 1-3 (fetch, parse, return links)
def extract_links(url: str) -> list[str]:
    """Fetch the page at `url`, parse it, and return the links found.

    [source: spec.md Summary, Inputs, Outputs, Acceptance criteria 1-3]
    """
    raise NotImplementedError
