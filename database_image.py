#!/usr/bin/python
import os
import sqlite3
from utils import SIFT
from utils import getImageHashValues
import numpy as np

conn = sqlite3.connect('datasets.db')
print("Opened database successfully")
c = conn.cursor()
KV = []

# images
c.execute("INSERT INTO DATASET (ID,NAME,TYPE,ADDRESS) \
      VALUES (2, 'Image Dataset', 'IMAGE', 'IMDS')")

c.execute('''CREATE TABLE IMDS
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME CHAR(20) NOT NULL,
        ADDRESS char(80) NOT NULL,
        HASH BLOB NOT NULL);''')

image_root = 'Image/mirflickr1m/images';
def getRelativePath(path):
    return path[path.find(image_root):]

def abs(x):
    if x < 0:
        return -x
    return x

def dis(a, b):
    d = 0
    for i in range(len(a)):
        d += abs(a[i]-b[i])
    return d

def nearest(v):
    min = 99999999999
    ans = []
    for s in KV:
        d = dis(s, v)
        if d < min:
            min = d
            ans = s
    return ans

def visitPath(path):
    list = os.listdir(path)
    for file in list:
        _path = path + '/' + file
        if os.path.isfile(_path):
            kpdes = SIFT(_path)
            vectors = kpdes[1]
            print('Old vector: ', vectors)
            vectors_new = []
            for v in vectors:
                vectors_new.append(nearest(v))
            print('New vector: ',vectors_new)
            hashvalue = getImageHashValues(vectors_new).tobytes()
            c.execute("insert into IMDS values (null, ?, ?, ?)", (file,  getRelativePath(_path), hashvalue))
            c.execute("insert into IMDS values (null, ?, ?, ?)", (file,  getRelativePath(_path), 0))
        else:
            visitPath(_path)

KV = np.load('Image/mirflickr1m/centroid/0-iteration.npy')
if os.path.exists(image_root):
    visitPath(image_root)
else:
    visitPath('../' + image_root)
conn.commit()
conn.close()