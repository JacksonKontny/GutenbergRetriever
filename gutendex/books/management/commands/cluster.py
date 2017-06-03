from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Prefetch, Avg, Count

from books import models, utils

from scipy.stats import pearsonr
from scipy.spatial.distance import cosine, jaccard, dice, euclidean

from sklearn.cluster import KMeans

import pandas as pd


def _db_handle(*args, **options):
    books = models.Book.objects.exclude(text='').annotate(
        sentence_count=Count('sentence'),
        average_pos=Avg('sentence__pos'),
        average_neg=Avg('sentence__neg'),
        average_neu=Avg('sentence__neu'),
        average_compound=Avg('sentence__compound')
    ).prefetch_related(
        Prefetch(
            'tokens',
            queryset=models.Posting.objects.select_related('token')
        )
    )
    tfidf_dict = {}
    tfidf_word_dict = {}
    polarity_dict = {}
    print('getting token tfidf')
    for idx, book in enumerate(books):
        tfidf_dict[book.pk] = book.sparse_tfidf_vector
        print("On book {}".format(idx))
    print('getting word tfidf')
    for idx, book in enumerate(books):
        tfidf_word_dict[book.pk] = book.sparse_word_tfidf_vector
        print("On book {}".format(idx))
    print('getting polarity')
    for idx, book in enumerate(books):
        print("On book {}".format(idx))
        polarity_dict[book.pk] = [
            book.average_pos,
            book.average_neg,
            book.average_neu,
            book.average_compound
        ]
    sparse_matrix = pd.DataFrame(tfidf_dict)
    sparse_matrix = sparse_matrix.T

    sparse_word_matrix = pd.DataFrame(tfidf_word_dict)
    sparse_word_matrix = sparse_word_matrix.T

    polarity_matrix = pd.DataFrame(tfidf_word_dict)
    polarity_matrix = polarity_matrix.T
    for matrix, cluster_type in [
        (sparse_matrix, models.Cluster.TOKENS),
        (sparse_word_matrix, models.Cluster.WORDS),
        (polarity_matrix, models.Cluster.POLARITY),
    ]:
        for n_clusters in [2, 5, 10, 20]:
            kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(matrix)
            for idx, label in enumerate(kmeans.labels_):
                book_pk = int(matrix.index[idx])
                models.Cluster.objects.update_or_create(
                    book=models.Book.objects.get(pk=book_pk),
                    n_clusters=n_clusters,
                    clustered_on=cluster_type,
                    defaults={'n': label},
                )


class Command(BaseCommand):
    help = 'This updates all item distances and store locally.'

    def handle(self, *args, **options):
        _db_handle()
