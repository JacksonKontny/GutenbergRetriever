from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from books import models, utils

from scipy.stats import pearsonr
from scipy.spatial.distance import euclidean


def _db_handle(*args, **options):
    books = models.Book.objects.exclude(text='').prefetch_related(
        Prefetch(
            'tokens',
            queryset=models.Posting.objects.select_related('token')
        )
    )
    big_dict = {}
    for idx, book in enumerate(books):
        big_dict[book.pk] = book.sparse_tfidf_vector
        print("On book {}".format(idx))
    book_pks = books.values_list('pk', flat=True)
    for idx, i in enumerate(book_pks):
        for j in book_pks[idx+1:]:
            # Correlation is same in both directions
            correlation = pearsonr(big_dict[i], big_dict[j])[0]
            models.Correlation.objects.update_or_create(
                book_1=models.Book.objects.get(pk=i),
                book_2=models.Book.objects.get(pk=j),
                distance=1-correlation
            )
            models.Correlation.objects.update_or_create(
                book_2=models.Book.objects.get(pk=i),
                book_1=models.Book.objects.get(pk=j),
                distance=1-correlation
            )
            euclidean_d = euclidean(big_dict[i], big_dict[j])
            models.Euclidean.objects.update_or_create(
                book_1=models.Book.objects.get(pk=i),
                book_2=models.Book.objects.get(pk=j),
                distance=euclidean_d
            )
            models.Euclidean.objects.update_or_create(
                book_2=models.Book.objects.get(pk=i),
                book_1=models.Book.objects.get(pk=j),
                distance=euclidean_d
            )


class Command(BaseCommand):
    help = 'This updates all item distances and store locally.'

    def handle(self, *args, **options):
        _db_handle()
