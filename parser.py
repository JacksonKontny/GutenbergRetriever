import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

'''
Read in book private key and text
'''
f = open('bookText.txt', 'r')
text = f.readlines() # book.pk %;% book.text
f.close()

'''
create a book dictionary
key: book.pk
value: list of stemmed word tokens
'''
book_dict = {}
ps = PorterStemmer()
stop_words = set(stopwords.words("english"))
for i in text:
    i = i.split('%;%') # these two lines are not universal. basically i[0] is the book.pk and i[1] is the book.text
    for j in string.punctuation:
        i[1] = i[1].replace(j, '')
    words = i[1].strip().split()
    lst = []
    # book_dict[int(i[0])] = [w.lower() for w in words if w.lower() not in stop_words]
    for w in words:
        if w.lower() not in stop_words and w.isalpha(): # filter out numbers
            try: # filter out non-word tokens
                lst.append(ps.stem(w))
            except IndexError:
                continue
    book_dict[int(i[0])] = lst

'''
create a posting list dictionary
key: token
value: dictionary of term frequency, doc frequency & doc# w/ freq
'''
listings = {}
for bookPK, wordList in book_dict.items():
    for word in wordList:
        if word not in listings:
            listings[word] = {}
            listings[word]['TF'] = 1
            listings[word]['DOC'] = {}
            listings[word]['DOC'][bookPK] = 1
            listings[word]['DF'] = 1
        elif word in listings:
            listings[word]['TF'] += 1
            if bookPK not in listings[word]['DOC']:
                listings[word]['DOC'][bookPK] = 1
                listings[word]['DF'] += 1
            elif bookPK in listings[word]['DOC']:
                listings[word]['DOC'][bookPK] += 1

output = open('vectorRep.csv', 'w')
output.write('Token, TF, DF, DOC\n')
for key, info in listings.items():
    to_write = key + ', ' + str(info['TF']) + ', ' + str(info['DF']) + ', '
    for bookPK, freq in info['DOC'].items():
        to_write += str(bookPK) + ':' + str(freq) + ' '
    to_write += '\n'
    output.write(to_write)
output.close()