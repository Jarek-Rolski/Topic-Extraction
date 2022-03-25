import datetime
from datetime import datetime

import pandas as pd

import gensim
from gensim.corpora import Dictionary
from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS

import spacy 

import pickle
import os
import sys
sys.path.append(os.path.join(os.environ['PWD'],'scripts'))

from scrap import get_comments

def preprocess_raw_comments(data):
    # Separate comments from ratings
    pos_text = []
    pos_cat = {}
    neg_text = []
    neg_cat = {}

    for review in data:
        pos_text.append(review[0][0])
    
        for cat in review[0][1]:
            if cat not in pos_cat.keys():
                pos_cat[cat] = 1
            else:
                pos_cat[cat] += 1
        
        neg_text.append(review[1][0])
    
        for cat in review[1][1]:
            if cat not in neg_cat.keys():
                neg_cat[cat] = 1
            else:
                neg_cat[cat] += 1
    
    # Ratings
    pos = pd.Series(pos_cat, name = 'pos')
    neg = pd.Series(neg_cat, name = 'neg')
    ratings = pd.merge(pos,neg, right_index = True, left_index = True, how='outer').sort_values('pos')
    
    # Comments
    # Load nlp pipeline
    nlp = spacy.load('en_core_web_sm')
    # Disable NER component
    nlp.disable_pipe('ner')
    # Add some stop words to improve analysis results
    nlp.Defaults.stop_words |= {'amazon','work','job','good'}
    
    pos_texts = []
    pos_texts_comment = []
    
    for comment in pos_text:
        comment = nlp(comment)
        text = []
        for word in comment:
            # Exclude special characters, stopwords, punctuations and numbers
            if len(word.text.replace(" ", "")) != 0 and word.text.replace(" ", "")[0] != "\r" and not word.is_stop\
            and not word.is_punct and not word.like_num:
                text.append(word.lemma_.lower().replace(" ", ""))
        
        if len(text) > 0:
            pos_texts.append(text)
            pos_texts_comment.append(comment)
       
    # Create bigrams, dictionary and corpus
    pos_bigram = Phrases(pos_texts, min_count=1, threshold=2, connector_words=ENGLISH_CONNECTOR_WORDS)
    pos_texts = [pos_bigram[line] for line in pos_texts]
    pos_dictionary = Dictionary(pos_texts)
    pos_corpus = [pos_dictionary.doc2bow(text) for text in pos_texts]
    
    neg_texts = []
    neg_texts_comment = []
    
    for comment in neg_text:
        comment = nlp(comment)
        text = []
        for word in comment:
            # Exclude special characters, stopwords, punctuations and numbers
            if len(word.text.replace(" ", "")) != 0 and word.text.replace(" ", "")[0] != "\r" and not word.is_stop\
            and not word.is_punct and not word.like_num:
                text.append(word.lemma_.lower().replace(" ", ""))
        
        if len(text) > 0:
            neg_texts.append(text)
            neg_texts_comment.append(comment)
            
    # Create bigrams, dictionary and corpus
    neg_bigram = Phrases(neg_texts, min_count=1, threshold=2, connector_words=ENGLISH_CONNECTOR_WORDS)
    neg_texts = [neg_bigram[line] for line in neg_texts]
    neg_dictionary = Dictionary(neg_texts)
    neg_corpus = [neg_dictionary.doc2bow(text) for text in neg_texts]
    
    data = {}
    data['ratings'] = ratings
    
    data['pos_texts'] = pos_texts
    data['pos_dictionary'] = pos_dictionary
    data['pos_corpus'] = pos_corpus
    data['pos_texts_comment'] = pos_texts_comment
    
    data['neg_texts'] = neg_texts
    data['neg_dictionary'] = neg_dictionary
    data['neg_corpus'] = neg_corpus
    data['neg_texts_comment'] = neg_texts_comment
    
    return data