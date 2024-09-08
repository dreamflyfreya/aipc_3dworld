from unidecode import unidecode
from django.template.defaultfilters import slugify

def unidecode_slugify(value):
    return 'empty-title' if not value else slugify(unidecode(value))
