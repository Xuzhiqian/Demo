#!/usr/bin/python
import os
import sqlite3

conn = sqlite3.connect('datasets.db')
print("Opened database successfully")
c = conn.cursor()

# images
c.execute("INSERT INTO DATASET (ID,NAME,TYPE,ADDRESS) \
      VALUES (2, 'Image Dataset', 'IMAGE', 'IMDS')")

c.execute('''CREATE TABLE IMDS
        (ID PRIMARY KEY INT NOT NULL,
        NAME CHAR(20) NOT NULL,
        ADDRESS char(50) NOT NULL,
        HASH BLOB NOT NULL);''')

def visitPath(path):
    list = os.listdir(path)
    for file in list:
        _path = path + '/' + file
        if os.path.isfile(_path):
            c.execute("insert into IMDS values (?, ?, ?, ?)", ('', file, _path, b'0'))
        else:
            visitPath(_path)

visitPath('Image/mirflickr1m/images')
conn.commit()
conn.close()