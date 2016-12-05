import template_remover
from bs4 import BeautifulSoup


def clean_string(text):
    text = template_remover.clean(text)
    bs = BeautifulSoup(text, "html.parser")
    return " ".join(s for s in bs.stripped_strings
                    if "amcharts" not in s.lower()).strip()
