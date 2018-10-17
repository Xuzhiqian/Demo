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
      VALUES (3, 'Vedio Dataset', 'VEDIO', 'VDS')")

c.execute('''CREATE TABLE VDS
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME CHAR(20) NOT NULL,
        ADDRESS char(80) NOT NULL,
        HASH BLOB NOT NULL);''')

vedio_root = 'Vedio/moments-in-time/Moments_in_Time_Mini';
def getRelativePath(path):
    return path[path.find(vedio_root):]

def visitPath(path):
    list = os.listdir(path)
    for file in list:
        _path = path + '/' + file
        if os.path.isfile(_path):
            # kpdes = SIFT(_path)
            # hashvalue = getImageHashValues(kpdes[1])
            # if hashvalue == 'error':
               # hashvalue = 0
            # else:
             #   hashvalue = hashvalue.tobytes()

            # c.execute("insert into IMDS values (null, ?, ?, ?)", (file,  getRelativePath(_path), hashvalue))
            c.execute("insert into VDS values (null, ?, ?, ?)", (file,  getRelativePath(_path), 0))
        else:
            visitPath(_path)

if os.path.exists(vedio_root):
    visitPath(vedio_root)
else:
    visitPath('../' + vedio_root)
conn.commit()
conn.close()