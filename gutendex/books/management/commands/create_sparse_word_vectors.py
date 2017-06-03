from django.core.management.base import BaseCommand

from books import models, utils
from collections import Counter


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        books = models.Book.objects.filter(
            has_word_vector=False, text__isnull=False, title__isnull=False
        ).exclude(
            text='',
        ).exclude(
            title='',
        )
        print(books.count())
        for idx, book in enumerate(books):
            print(idx, book.title)
            text = book.text
            pk = book.pk

            counter = utils.get_word_count(text, stem=False)
            utils.create_postings(book, counter, tokenized=False)

            book.has_word_vector = True
            book.save(update_fields=['has_word_vector'])
