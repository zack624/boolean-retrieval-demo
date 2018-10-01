# -*- coding: utf-8 -*-


import pickle
import re
from bitarray import bitarray


# data pre-processing,return article(dictionary) and art_id list
def load_dataset(path):
    import os
    import json
    articles = []
    files = os.listdir(path)
    for f in files:
        f_path = os.path.join(path, f)
        fo = open(f_path)
        for line in fo.readlines():
            article = json.loads(line)
            articles.append(article)
    return articles


def data_pre_processing(dataset):
    split_dataset = dataset[:]
    for article in split_dataset:
        # FIXME split content to words
        content = article['content']
        # change_u = re.sub('’'.decode('utf-8'), "'", content)
        del_u = re.sub('[—“”‘’]'.decode('utf-8'), " ", content)
        no_punc_content = re.sub(r'[,\.?:;!()\[\]\']', " ", del_u.strip())
        not_next_line = re.sub(r'[\n\"/]', " ", no_punc_content)
        # del_single = re.sub(r"(\s'|'\s)", " ", not_next_line)
        not_continue_space = re.sub(r'\s+', " ", not_next_line)
        words = not_continue_space.split(' ')
        article['content'] = set([w.lower() for w in words])
    return split_dataset


# create word list
def create_word_list(dataset):
    word_list = set([])
    for article in dataset:
        word_list = word_list | article['content']
    # remove not english words
    words = []
    for word in word_list:
        rs = re.match(r'[a-z-]+', word)
        if rs and rs.group() == word:
            words.append(word)
            continue
        rs = re.match(r'[0-9-]+', word)
        if rs and rs.group() == word:
            words.append(word)
    return words[1:]


def save_word_list(word_list, file_name):
    pickle.dump(word_list, open(file_name, 'wb'))


def load_word_list(file_name):
    return pickle.load(open(file_name, 'rb'))


# create word vectors from documents and save them
def create_word_vectors(dataset, word_list):
    w_count = len(word_list)
    a_count = len(dataset)
    # word_vectors = mat(zeros((w_count, a_count)))
    word_vectors = []
    for i in range(w_count):
        if i % 10000 == 0:
            print len(word_list), " word vectors generating: ", i
        vector = bitarray(a_count)
        vector.setall(False)
        for j in range(a_count):
            if word_list[i] in dataset[j]['content']:
                # word_vectors[i, j] = 1
                vector[j] = True
        word_vectors.append(vector)
    return word_vectors


def save_word_vectors(word_vectors, file_name):
    # save(file_name, word_vectors)
    fr = open(file_name, "w")
    fr.write(str(word_vectors))


def load_word_vectors(file_name):
    # return load(file_name)
    fr = open(file_name, "r")
    return eval(fr.read())


# match query and return document list
def find_word_vector(word, word_list, word_vectors):
    try:
        index = word_list.index(word.lower())
    except ValueError:
        raise
    # return word_vectors[index, :]
    return word_vectors[index]


def retrieval(query, word_list, word_vectors, dataset):
    try:
        queries = query.strip().split(' ')
        if queries[0] != 'NOT':
            query_vector = find_word_vector(queries[0], word_list, word_vectors)
        else:
            query_vector = find_word_vector(queries[1], word_list, word_vectors)
            # query_vector = (query_vector-1)*-1
            query_vector = ~query_vector
        for i in range(1, len(queries)):
            if queries[i] == 'AND' or queries[i] == 'OR' or queries[i] == 'NOT':
                post = find_word_vector(queries[i+1], word_list, word_vectors)
                if queries[i] == 'AND':
                    # query_vector = multiply(query_vector, post)
                    query_vector = query_vector & post
                if queries[i] == 'OR':
                    # query_vector = add(query_vector, post)
                    query_vector = query_vector | post
                if queries[i] == 'NOT':
                    # query_vector = multiply(query_vector, (post-1)*-1)
                    query_vector = query_vector & ~post
        # FIXME to use function nonzero
        query_art = []
        for i in range(len(dataset)):
            if query_vector[i] == 1:
                query_art.append(dataset[int(i)])
    except ValueError:
        return []
    return query_art


def initial(dataset, word_list_name, vector_name):
    split_ds = data_pre_processing(dataset)
    wl = create_word_list(split_ds)
    save_word_list(wl, word_list_name)
    wv = create_word_vectors(split_ds, wl)
    save_word_vectors(wv, vector_name)


def search(dataset, word_list_name, vector_name):
    word_list = load_word_list(word_list_name)
    word_vectors = load_word_vectors(vector_name)
    while True:
        search_words = raw_input("please input your search words:")
        articles = retrieval(search_words, word_list, word_vectors, dataset)
        for a in articles:
            print "id: ", str(a['id']), "title: ", a['title']
        print "count: ", len(articles)
        print "=" * 100


if __name__ == '__main__':
    dataset = load_dataset('dataset')
    # initial(dataset, "5001word_list.txt", "5001word_vectors_real_bit.txt")
    search(dataset, "5001word_list.txt", "5001word_vectors_real_bit.txt")
