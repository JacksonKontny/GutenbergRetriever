Gutenberg Retriever
==============

It is probably best to view this readme from the [github repo](https://github.com/JacksonKontny/GutenbergRetriever)

This project is a prototype information retrieval system and item based recommender system for
books hosted on Project Gutenberg.  It builds off the work of two open source projects, the
[gutendex django project](https://github.com/garethbjohnson/gutendex), and the 
[python gutenberg library](https://pypi.python.org/pypi/Gutenberg). See gutendex/gutendex_readme.md for
information about the gutendex django project, which got our project off to a strong start.

Gutendex Prep
-------------

If you intend to get our project running on your own machine, it is probably best you
follow the [gutendex installation guide](https://github.com/garethbjohnson/gutendex/wiki/Installation-Guide) before you
continue stopping at Step 8.  DO NOT FOLLOW (Step 3. Install Python Packages) - you'll want to install [anaconda](https://www.continuum.io/downloads) instead.
Once you have anaconda installed, you can start a new environment and activate it as follows (from bash terminal in gutendex directory):

conda create -n yourenvname python=3.5 anaconda
source activate yourenvname
while read requirement; do conda install --yes $requirement; done < requirements.txt

You can now proceed...

Adding Book Text to the Database
--------------------------------

DISCLAIMER: All of the commands take a long time. If you wish to speed the process,
modify BOOK_COUNT in gutendex/books/management/commands/updatebooks.py to a small number.  You will
pull fewer books, but will be able to demo the project with a small(er) sacrifice of your time.

At present, Project Gutenberg offers over 53,000 books on its website.  The open source
gutendex project made it easy to pull the catalog information for Project Gutenberg, but
did not pull the text of the books, or clean the legal information.  We borrowed some
code from the python gutenberg library to help with this.  The code for pulling actual
text into the database can be seen in gutendex/books/management/commands/updatebooks.py

To pull the book text from project gutenberge, execute the following from you bash terminal while in the anaconda virtual environment in the gutendex home directory:
python manage.py updatebooks

This will populate the first 100 books in the gutenberg catalog.  If you wish to acquire a different
number of books, you can do so by editing the BOOK_COUNT variable in updatebooks.py

Adding Postings and Tokens to the Database
------------------------------------------

Once the actual text is populated in your database, you need a way to quickly search
that text for relevant information.  We added several new tables/models to the database
in order to store unique tokens accross all books, their document frequency, and their
term frequency in each respective book.  All models can be seen in gutendex/books/management/commands/models.py.
The code for updating the postings and tokens from the book text can be seen in 
gutendex/books/management/commands/parse.py.  Several utilities were also added to gutendex/books/utils.py
to help with this process.

To parse the book text information and add postings and token information to you database, execute the following:
python manage.py parse

Caching Book Similarity
-----------------------

With the Postings and Tokens populated in your database, you are ready to use the query portion of the website.  But before
you do so, if you desire to also demo the item based recommender portion of the website, we suggest you start the distance caching
process as soon as possible.

The distance caching process computes the Cosine, Jaccard, Pearson, Euclidean, and Dice distance between each book in the dataset.
Since this computation takes too long to be practical for searching, we perform the computation ahead of time and cache the
distance values in our database.  These values are stored via the Distance and DistanceType models in
gutendex/books/models.py.  To perform the caching process, execute:
python manage.py recommend

While that's running, assuming our server is still running (if it isn't execute `python manage.py runserver` to get it started)
you can navigate to localhost:8000/books/query in your browser to demo the query system.

Once the 'recommend' function is finished, you can also demo the item based recommender.  To demo the recommender,
you can navigate to localhost:8000/books/recommend/

Running Evaluation
------------------

You may also wish to run evaluation for yourself.  To do this, you will want to create a separate database so as not to
intermix the Time articles in the evaluation dataset with the Books from project gutenberg.  To do so, follow the 'Make Database'
instructions from the [gutendex installation guide](https://github.com/garethbjohnson/gutendex/wiki/Installation-Guide), substiting
'gutendex' with 'gutendex_eval'.  Once you have your new database, you will also want to edit the .env configuration file in gutendex/.env
with the following configuration parameter:

DATABASE_NAME=gutendex_eval

Now that your project is pointing to a different database, you can upload the Time dataset by executing the following management command:
python manage.py updatebooksevaluation

Now that the evaluation dataset is loaded in your database, you can generate the ranked document predictions by running:
python manage.py evaluation

The predictions will be output in several csv files from which you can perform any analysis, comparing the results to those
found in gutendex/books/evaluation/time/TIME.REL
