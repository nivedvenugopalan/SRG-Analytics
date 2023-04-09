from langdetect import detect
from translate import Translator


def detect_language(text: str) -> str:
    return detect(text)


translator = Translator(to_lang='en')


def translate(text: str) -> str:
    return translator.translate(text)
