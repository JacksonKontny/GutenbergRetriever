from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from books import models, utils

from scipy.stats import pearsonr
from scipy.spatial.distance import cosine, jaccard, dice, euclidean


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
    book_pks = [x for x in tfidf_dict.keys()]
    for idx, i in enumerate(book_pks):
        book_i_vector = tfidf_dict[i]
        book_i = models.Book.objects.get(pk=i)
        for j in book_pks[idx+1:]:
            book_j_vector = tfidf_dict[j]
            book_j = models.Book.objects.get(pk=j)
            pearson_distance = 1 - pearsonr(book_i_vector, book_j_vector)[0]
            euclidean_distance = euclidean(book_i_vector, book_j_vector)
            cosine_distance = cosine(book_i_vector, book_j_vector)
            jaccard_distance = jaccard(book_i_vector, book_j_vector)
            dice_distance = dice(book_i_vector, book_j_vector)
            euclidean_type = models.DistanceType.objects.get(
                code=models.DistanceType.EUCLIDEAN
            )
            models.Distance.objects.update_or_create(
                book_1=book_i,
                book_2=book_j,
                distance_type=euclidean_type,
                defaults={'distance': euclidean_distance},
            )
            models.Distance.objects.update_or_create(
                book_1=book_j,
                book_2=book_i,
                distance_type=euclidean_type,
                defaults={'distance': euclidean_distance},
            )
            pearson_type = models.DistanceType.objects.get(
                code=models.DistanceType.PEARSON
            )
            models.Distance.objects.update_or_create(
                book_1=book_i,
                book_2=book_j,
                distance_type=pearson_type,
                defaults={'distance': pearson_distance},
            )
            models.Distance.objects.update_or_create(
                book_1=book_j,
                book_2=book_i,
                distance_type=pearson_type,
                defaults={'distance': pearson_distance},
            )
            cosine_type = models.DistanceType.objects.get(
                code=models.DistanceType.COSINE
            )
            models.Distance.objects.update_or_create(
                book_1=book_i,
                book_2=book_j,
                distance_type=cosine_type
            )
            models.Distance.objects.update_or_create(
                book_1=book_j,
                book_2=book_i,
                distance_type=cosine_type,
                defaults={'distance': cosine_distance},
            )
            jaccard_type = models.DistanceType.objects.get(
                code=models.DistanceType.JACCARD
            )
            models.Distance.objects.update_or_create(
                book_1=book_i,
                book_2=book_j,
                distance_type=jaccard_type,
                defaults={'distance': jaccard_distance},
            )
            models.Distance.objects.update_or_create(
                book_1=book_j,
                book_2=book_i,
                distance_type=jaccard_type,
                defaults={'distance': jaccard_distance},
            )
            dice_type = models.DistanceType.objects.get(
                code=models.DistanceType.DICE
            )
            models.Distance.objects.update_or_create(
                book_1=book_i,
                book_2=book_j,
                distance_type=dice_type,
                defaults={'distance': dice_distance},
            )
            models.Distance.objects.update_or_create(
                book_1=book_j,
                book_2=book_i,
                distance_type=dice_type,
                defaults={'distance': dice_distance},
            )
            print(i, j)



class Command(BaseCommand):
    help = 'This updates all item distances and store locally.'

    def handle(self, *args, **options):
        _db_handle()
