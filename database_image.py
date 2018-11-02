#!/usr/bin/python
import os
import sqlite3
from utils import SIFT
from utils import getImageHashValues
import numpy as np

conn = sqlite3.connect('datasets.db')
print("Opened database successfully")
c = conn.cursor()

# images
c.execute("INSERT INTO DATASET (ID,NAME,TYPE,ADDRESS) \
      VALUES (2, 'Image Dataset', 'IMAGE', 'IMDS')")

c.execute('''CREATE TABLE IMDS
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME CHAR(20) NOT NULL,
        ADDRESS char(80) NOT NULL,
        HASH BLOB NOT NULL);''')

image_root = 'Image/mirflickr1m/images';
log = open("error_image.txt","w")
def getRelativePath(path):
    return path[path.find(image_root):]

def visitPath(path):
    list = os.listdir(path)
    for file in list:
        _path = path + '/' + file
        if os.path.isfile(_path):
            try:
                kpdes = SIFT(_path)
                hashvalue = getImageHashValues(kpdes[1]).tobytes()
                c.execute("insert into IMDS values (null, ?, ?, ?)", (file,  getRelativePath(_path), hashvalue))
            except Exception as e:
                print(e,file=log)
                print('Image :',_path,file=log)
                print('Image :',_path)
                c.execute("insert into IMDS values (null, ?, ?, ?)", ('error_image', getRelativePath(_path), 0))
        else:
            visitPath(_path)

if os.path.exists(image_root):
    visitPath(image_root)
else:
    visitPath('../' + image_root)
log.close()
conn.commit()
conn.close()