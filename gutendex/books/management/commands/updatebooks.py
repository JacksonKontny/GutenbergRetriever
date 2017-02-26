import os
from time import strftime
import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from gutenberg.cleanup import strip_headers

from books import utils, models


BOOK_COUNT = 100


# Heavily influenced by Gutenberg library @https://pypi.python.org/pypi/Gutenberg
def fetch_etext(etextno):
    """Returns a unicode representation of the full body of a Project Gutenberg
    text. After making an initial remote call to Project Gutenberg's servers,
    the text is persisted locally.

    """
    download_uri = _format_download_uri(etextno)
    if download_uri:
        response = requests.get(download_uri)
        return strip_headers(response.text.strip()).encode('utf-8')
    return ''


def _format_download_uri(etextno):
    """Returns the download location on the Project Gutenberg servers for a
    given text.

    Raises:
        UnknownDownloadUri: If no download location can be found for the text.

    """
    uri_root = r'http://www.gutenberg.lib.md.us'
    extensions = ('.txt', '-8.txt', '-0.txt')
    for extension in extensions:
        path = _etextno_to_uri_subdirectory(etextno)
        uri = '{root}/{path}/{etextno}{extension}'.format(
            root=uri_root,
            path=path,
            etextno=etextno,
            extension=extension)
        response = requests.head(uri)
        if response.ok:
            return uri

def _etextno_to_uri_subdirectory(etextno):
    """
    For example, ebook #1 is in subdirectory:
    0/1

    And ebook #19 is in subdirectory:
    1/19

    While ebook #15453 is in this subdirectory:
    1/5/4/5/15453
    """
    str_etextno = str(etextno).zfill(2)
    all_but_last_digit = list(str_etextno[:-1])
    subdir_part = "/".join(all_but_last_digit)
    subdir = "{0}/{1}".format(subdir_part, etextno)  # etextno not zfilled
    return subdir



class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        for book in models.Book.objects.filter(
                languages__code='en', # get all english books
                gutenberg_id__gt=0, # gutenberg ids have to be greater than 0
                media_type='Text', # we only want books!
        ).order_by('gutenberg_id')[:BOOK_COUNT]:
            book_text = fetch_etext(book.gutenberg_id)
            book.text = book_text
            book.save()
