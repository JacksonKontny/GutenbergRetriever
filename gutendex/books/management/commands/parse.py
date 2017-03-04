from django.core.management.base import BaseCommand

from books import models, utils
from collections import Counter


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        for book in models.Book.objects.filter(
            is_parsed=False,
        ).exclude(
            text=''
        ):
            text = book.text
            pk = book.pk

            counter = utils.get_word_count(text)

            for word, count in counter.items():
                token, created = models.Token.objects.get_or_create(
                    name=word
                )
                token.total_occurances += count
                token.df += 1
                token.save()

                models.Posting.objects.create(
                    book=book,
                    token=token,
                    tf = count,
                )
            book.is_parsed = True
            book.save()
