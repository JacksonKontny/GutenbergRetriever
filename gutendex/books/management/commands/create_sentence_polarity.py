from django.core.management.base import BaseCommand
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from books import models, utils
from collections import Counter


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        books = models.Book.objects.filter(
            text__isnull=False, title__isnull=False
        ).exclude(
            text='',
        ).exclude(
            title='',
        )
        sid = SentimentIntensityAnalyzer()
        print(books.count())
        for idx, book in enumerate(books):
            print(idx, book.title)
            pk = book.pk
            sentences = tokenize.sent_tokenize(book.text)
            for idx, sentence in enumerate(sentences):
                if idx == 1:
                    print(sentence)
                ss = sid.polarity_scores(sentence)
                ss['index'] = idx
                ss['book_id'] = book.pk
                models.Sentence.objects.create(**ss)
