from mat.mat import nlp


def analyze_sentiment(text: str) -> float:
    doc = nlp(text)
    return (doc.sentiment)
