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
      VALUES (3, 'Video Dataset', 'VIDEO', 'VDS')")

c.execute('''CREATE TABLE VDS
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME CHAR(20) NOT NULL,
        ADDRESS char(80) NOT NULL);''')

video_root = 'Video/moments-in-time/Moments_in_Time_Mini/training';
def getRelativePath(path):
    return path[path.find(video_root):]

def visitPath(path):
    list = os.listdir(path)
    for file in list:
        _path = path + '/' + file
        if os.path.isfile(_path):
            c.execute("insert into VDS values (null, ?, ?)", (file,  getRelativePath(_path)))
        else:
            visitPath(_path)

if os.path.exists(video_root):
    visitPath(video_root)
else:
    visitPath('../' + video_root)
conn.commit()
conn.close()