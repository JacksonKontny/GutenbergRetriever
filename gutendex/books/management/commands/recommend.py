from django.core.management.base import BaseCommand

from books import models, utils

class Command(BaseCommand):
    help = 'This updates all item distances and store locally.'

    def handle(self, *args, **options):
        book_id = []
        for book in models.Book.objects.exclude(text=''):
            book_id.append(book.id)

        for i in book_id:
            for j in book_id[book_id.index(i)+1:]:
                book_1 = models.Book.objects.filter(id=i)[0]
                book_2 = models.Book.objects.filter(id=j)[0]
                book_1_tokens = list(book_1.posting_set.values_list(
                                                            'token_id', flat=True
                                                            ).order_by('token_id'))
                book_2_tokens = list(book_2.posting_set.values_list(
                                                            'token_id', flat=True
                                                            ).order_by('token_id'))
                all_tokens = set(book_1_tokens+book_2_tokens)
                n = len(all_tokens)

                book_1_vector_tfidf = []
                book_2_vector_tfidf = []

                for tok_id in all_tokens:
                    if tok_id in book_1_tokens:
                        book_1_vector_tfidf.append(book_1.posting_set.filter(token_id=tok_id)[0].tfidf)
                    else:
                        book_1_vector_tfidf.append(0)

                    if tok_id in book_2_tokens:
                        book_2_vector_tfidf.append(book_2.posting_set.filter(token_id=tok_id)[0].tfidf)
                    else:
                        book_2_vector_tfidf.append(0)

                print(utils.get_corr(book_1_vector_tfidf, book_2_vector_tfidf))