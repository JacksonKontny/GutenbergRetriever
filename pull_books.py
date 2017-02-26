from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg.query import get_metadata

METADATA_LIST = [
    u'author', u'formaturi', u'language', u'rights', u'subject', u'title'
]
BOOKS_TO_PULL = 10

for book_index in xrange(1, BOOKS_TO_PULL):
    text = strip_headers(load_etext(book_index)).strip()
    meta_dict = {}
    for metatype in METADATA_LIST:
        metadata = get_metadata(metadata, book_index)
        meta_dict[metatype] = metadata
        print metadata,

    print text[-50:]
    print meta_dict

