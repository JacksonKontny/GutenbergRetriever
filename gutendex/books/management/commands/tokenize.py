from django.core.management.base import BaseCommand

from books import models, utils
from collections import Counter


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        books = models.Book.objects.filter(
            is_parsed=False,
        ).exclude(
            text=''
        )
        print(books.count())
        for idx, book in enumerate(books):
            print(idx, book.title)
            text = book.text
            pk = book.pk

            counter = utils.get_word_count(text)
            utils.create_postings(book, counter)

            book.is_parsed = True
            book.save()
