from collections import Counter
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from keras.utils import to_categorical

MAX_LEN = 100 
PAD_STRING = '--PAD--'
NUM_CATEGORIES = 8


def pad_tokenize(text):
    tokens = text.split()
    tokens = tokens[:MAX_LEN]
    if len(tokens) < MAX_LEN:
        pads = MAX_LEN - len(tokens)
        tokens += [PAD_STRING] * pads
    assert len(tokens) == MAX_LEN
    return np.array(tokens, dtype=str)

names = ['text', 'tag']
df = pd.read_csv('new_new.csv', names=names)

c = Counter(df.tag)

idx_to_label = {}
label_to_idx = {}

labels = [x[0] for x in c.most_common()[3: 3 + NUM_CATEGORIES]]
for i, label in enumerate(labels):
    idx_to_label[i] = label
    label_to_idx[label] = i

def map_label(label):
    return label_to_idx[label]

subsample = df[df.tag.isin(labels)] 

subsample = subsample.replace(np.nan, '')
subsample['str len'] = subsample['text'].map(str).apply(len)
subsample['tag_id'] = subsample['tag'].apply(map_label)

train, test = train_test_split(subsample, test_size=0.2)

x_train = np.array([pad_tokenize(x) for x in train['text'].values])
y_train = to_categorical(train['tag_id'].values)
x_test = np.array([pad_tokenize(x) for x in test['text'].iloc[:].values])
y_test = to_categorical(test['tag_id'].values)