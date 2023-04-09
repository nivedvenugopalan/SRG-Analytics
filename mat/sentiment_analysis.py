from mat.mat import nlp


def analyze_sentiment(text: str) -> tuple[float]:
    doc = nlp(text)
    return (doc.sentiment.polarity, doc.sentiment.subjectivity)
