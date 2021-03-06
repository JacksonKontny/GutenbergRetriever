from django.core.management.base import BaseCommand
from cProfile import Profile

from books import utils, models


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        models.Token.objects.all().delete()
        models.Book.objects.all().delete()
        with open('books/evaluation/time/TIME.ALL', 'r') as text_data:
            lines = [
                line.strip() for line in text_data.readlines() if line.strip() != ''
            ]
            doc_number = 0
            doc_name = ''
            book_lines = []
            for line in lines:
                if line.startswith('*TEXT'):
                    if book_lines:
                        text = '\n'.join(book_lines)
                        book, _ = models.Book.objects.update_or_create(
                            gutenberg_id=doc_number,
                            title=doc_name,
                            text=text
                        )
                        counter = utils.get_word_count(text)
                        utils.create_postings(book, counter)
                        book.is_parsed=True
                        book.save()
                    book_lines = []
                    doc_name = line
                    doc_number += 1
                    print(doc_number)
                else:
                    if '*STOP' not in line:
                        book_lines.append(line)
                    else:
                        text = '\n'.join(book_lines)
                        book, _ = models.Book.objects.update_or_create(
                            gutenberg_id=doc_number,
                            title=doc_name,
                            text=text
                        )
                        counter = utils.get_word_count(text)
                        utils.create_postings(book, counter)
                        book.is_parsed=True
                        book.save()
