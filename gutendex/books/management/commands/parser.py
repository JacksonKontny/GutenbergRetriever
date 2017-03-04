import string
from django.core.management.base import BaseCommand
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from books import models
from collections import Counter


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        ps = PorterStemmer()
        stop_words = set(stopwords.words("english"))
        for book in models.Book.objects.filter(
            is_parsed=False,
        ).exclude(
            text=''
        ):
            text = book.text
            pk = book.pk
            for punc in string.punctuation:
                text = text.replace(punc, ' ')

            words = text.strip().split()

            stemmed_words = []
            for w in words:
                try:
                    w = ps.stem(w)
                    if w.lower() not in stop_words and w.isalpha():
                        stemmed_words.append(w)
                except IndexError:
                    continue

            counter = Counter(stemmed_words)

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
