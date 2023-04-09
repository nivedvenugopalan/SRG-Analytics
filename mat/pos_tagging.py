from mat.mat import nlp

from spacy import displacy
from PIL import Image
from io import BytesIO


def get_pos_tagged_img(text: str) -> BytesIO:
    doc = nlp(text)
    img = displacy.render(doc, style='dep', jupyter=False)

    img_bytes = BytesIO()
    Image.open(img).save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes
