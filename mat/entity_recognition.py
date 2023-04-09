from mat.mat import nlp


def get_entities(text: str) -> list[tuple[str, str]]:
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]
