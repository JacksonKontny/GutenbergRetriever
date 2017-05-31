from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from books import models, utils

from scipy.stats import pearsonr
from scipy.spatial.distance import cosine, jaccard, dice, euclidean

from sklearn.cluster import KMeans

import pandas as pd


def _db_handle(*args, **options):
    books = models.Book.objects.exclude(text='').prefetch_related(
        Prefetch(
            'tokens',
            queryset=models.Posting.objects.select_related('token')
        )
    )
    tfidf_dict = {}
    for idx, book in enumerate(books):
        tfidf_dict[book.pk] = book.sparse_tfidf_vector
        print("On book {}".format(idx))
    sparse_matrix = pd.DataFrame(tfidf_dict)
    kmeans = KMeans(n_clusters=10, random_state=0).fit(sparse_matrix)


class Command(BaseCommand):
    help = 'This updates all item distances and store locally.'

    def handle(self, *args, **options):
        _db_handle()
