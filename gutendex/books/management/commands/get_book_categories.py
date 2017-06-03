import os
from time import strftime
import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from gutenberg.cleanup import strip_headers

from books import utils, models
from books.management.commands.updatebooks import (
    fetch_etext,
    _format_download_uri,
    _etextno_to_uri_subdirectory
)

# A handful of arbitrary categories
CATEGORIES = [
    'Art',
    'Birds',
    'Ethics',
    'Ghosts',
    'Success',
    'Vegetarianism',
    'War',
    'Women',
    'Utopias'
    'Zoology'
]

# A handful of arbitrary subcategories
SUBCATEGORIES = [
    'World War, 1914-1918 -- Aerial operations',
    'World War, 1914-1918 -- Campaigns -- Western Front',
    'World War, 1914-1918 -- Causes',
    'World War, 1914-1918 -- England -- Fiction',
    'World War, 1914-1918 -- France',
    'World War, 1914-1918 -- Naval operations',
    'World War, 1914-1918 -- Periodicals',
    'World War, 1914-1918 -- Personal narratives',
    'World War, 1914-1918 -- Poetry',
    'World War, 1914-1918 -- Prisoners and prisons, German',
    'World War, 1914-1918 -- Regimental histories -- Great Britain',
    'World War, 1914-1918 -- United States',
]


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        for category in CATEGORIES:
            print('getting text for {}:'.format(category))
            self._get_category_etext(category, CATEGORIES)
        for subcategory in SUBCATEGORIES:
            print('getting text for {}:'.format(subcategory))
            self._get_category_etext(subcategory, SUBCATEGORIES)

    def _get_category_etext(self, category, categories):
        count=0
        for book in models.Book.objects.filter(
            languages__code='en', # get all english books
            gutenberg_id__gt=0, # gutenberg ids have to be greater than 0
            media_type='Text', # we only want books!
            text='', # we only want books we haven't grabbed text for
            subjects__name=category
        ).exclude(
            subjects__name__in=list(set(categories) - set([category]))
        ).order_by('gutenberg_id')[:10]:
            print('\t' + book.title)
            book_text = fetch_etext(book.gutenberg_id)
            if book_text != '':
                book.text = book_text
                book.save()
            else:
                print('failure')
        print(count)
