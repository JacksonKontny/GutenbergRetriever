import csv
from cProfile import Profile
from django.core.management.base import BaseCommand
from collections import defaultdict

from books import utils, models
from books.views import get_ranked_books


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile',
            action='store_true',
            help="Only check order and cpt codes.  Doesn't update files",
        )

    def _handle(self, *args, **options):
        metric_mapping = {
            '0': 'cosine_distance',
            '1': 'jaccard_distance',
            '2': 'dice_coefficient',
        }
        transformation_mapping = {
            '0': 'tfidf',
            '1': '', # No tranformation
            '2': 'binary',
        }
        with open('books/evaluation/time/TIME.QUE', 'r') as text_data:
            lines = [
                line.strip() for line in text_data.readlines() if line.strip() != ''
            ]
            query_number = 0
            query_lines = []
            csvs = defaultdict(list)
            for line in lines:
                if line.startswith('*FIND'):
                    if query_lines:
                        query = ' '.join(query_lines)

                        # Perform the query

                        for distance_key, distance_name in metric_mapping.items():
                            for trans_key, trans_name in transformation_mapping.items():
                                rank = get_ranked_books(
                                    query,
                                    distance_key,
                                    trans_key,
                                    limit=models.Book.objects.count()
                                )
                                documents = []
                                for pk in rank:
                                    book = models.Book.objects.get(pk=pk)
                                    documents.append(book.gutenberg_id)

                                csv_name = '{}_{}.csv'.format(distance_name, trans_name)
                                result = [query_number]
                                result.extend(documents)
                                csvs[csv_name].append(result)
                        break

                    query_lines = []
                    query_number += 1
                    print(query_number)

                else:
                    if '*STOP' not in line:
                        query_lines.append(line)

            for csv_name, rows in csvs.items():
                with open(csv_name, 'w') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',')
                    for row in rows:
                        csv_writer.writerow(row)

    def handle(self, *args, **options):
        if options['profile']:
            profiler = Profile()
            profiler.runcall(self._handle, *args, **options)
            profiler.print_stats()
        else:
            self._handle(*args, **options)
