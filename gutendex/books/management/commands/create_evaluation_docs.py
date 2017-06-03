from django.core.management.base import BaseCommand
from django.db.models import Count, Avg
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

from books import models, utils
from books.management.commands.get_book_categories import CATEGORIES, SUBCATEGORIES
from collections import Counter


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        books = models.Book.objects.annotate(
            sentence_count=Count('sentence'),
            average_pos=Avg('sentence__pos'),
            average_neg=Avg('sentence__neg'),
            average_neu=Avg('sentence__neu'),
            average_compound=Avg('sentence__compound')
        ).filter(
            text__isnull=False, title__isnull=False
        ).filter(
            sentence_count__gt=0
        ).exclude(
            text='',
        ).exclude(
            title='',
        )

        category_books = books.filter(subjects__name__in=CATEGORIES)
        subcategory_books = books.filter(subjects__name__in=SUBCATEGORIES)

        category_word_doc = {}
        category_token_doc = {}
        category_sentiment_doc = {}

        print('in category books: {}'.format(category_books.count()))
        # get book word vectors
        count=0
        for book in category_books:
            count += 1
            print(count)
            print(book.title)
            category_word_doc[book.pk] = book.sparse_word_tfidf_vector
            category_token_doc[book.pk] = book.sparse_tfidf_vector
            category_sentiment_doc[book.pk] = [
                book.average_pos,
                book.average_neg,
                book.average_neu,
                book.average_compound
            ]

            category = set(CATEGORIES) & set(
                book.subjects.values_list('name', flat=True)
            )
            category_token_doc[book.pk].append(category)
            category_word_doc[book.pk].append(category)
            category_sentiment_doc[book.pk].append(category)

        print('in subcategory books: {}'.format(category_books.count()))
        count = 0
        subcategory_word_doc = {}
        subcategory_token_doc = {}
        subcategory_sentiment_doc = {}
        for book in subcategory_books:
            count += 1
            print(count)
            print(book.title)
            subcategory_word_doc[book.pk] = book.sparse_word_tfidf_vector
            subcategory_token_doc[book.pk] = book.sparse_tfidf_vector
            subcategory_sentiment_doc[book.pk] = [
                book.average_pos,
                book.average_neg,
                book.average_neu,
                book.average_compound
            ]
            category = set(SUBCATEGORIES) & set(
                book.subjects.exclude(name__in=SUBCATEGORIES).values_list(
                    'name', flat=True
                )
            )
            subcategory_token_doc[book.pk].append(category)
            subcategory_word_doc[book.pk].append(category)
            subcategory_sentiment_doc[book.pk].append(category)

        category_word_df = pd.DataFrame(category_word_doc)
        category_token_df = pd.DataFrame(category_token_doc)
        category_sentiment_df = pd.DataFrame(category_sentiment_doc)

        category_word_df = category_word_df.T
        category_token_df = category_token_df.T
        category_sentiment_df = category_sentiment_df.T

        category_word_df.to_csv('output/category_word_tfidf.csv')
        category_token_df.to_csv('output/category_token_tfidf.csv')
        category_sentiment_df.to_csv('output/category_sentiment_tfidf.csv')

        subcategory_word_df = pd.DataFrame(subcategory_word_doc)
        subcategory_token_df = pd.DataFrame(subcategory_token_doc)
        subcategory_sentiment_df = pd.DataFrame(subcategory_sentiment_doc)

        subcategory_word_df = subcategory_word_df.T
        subcategory_token_df = subcategory_token_df.T
        subcategory_sentiment_df = subcategory_sentiment_df.T

        subcategory_word_df.to_csv('output/subcategory_word_tfidf.csv')
        subcategory_token_df.to_csv('output/subcategory_token_tfidf.csv')
        subcategory_sentiment_df.to_csv('output/subcategory_sentiment_tfidf.csv')
