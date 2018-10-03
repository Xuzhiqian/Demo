#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('datasets.db')
print("Opened database successfully")
c = conn.cursor()
c.execute('''CREATE TABLE DATASET
       (ID INT  PRIMARY KEY NOT NULL,
       NAME CHAR(100) NOT NULL,
       TYPE CHAR(20),      
       ADDRESS CHAR(50) NOT NULL);''')
print("Table created successfully")

# text
c.execute("INSERT INTO DATASET (ID,NAME,TYPE,ADDRESS) \
      VALUES (1, 'Large Movie Review Dataset', 'TEXT', 'LMRD_1')")
      
c.execute('''CREATE TABLE LMRD_1
       (CATEGORY CHAR(10) NOT NULL,
       FILEID CHAR(10) NOT NULL,
       DATA TEXT NOT NULL,     
       HASH BLOB NOT NULL);''')
print("Table created successfully")


cursor = c.execute("""SELECT * FROM sqlite_master WHERE type='table';""")
for i in cursor :
    print(i)

r = readpkl('Large-Movie-Review-Dataset.pkl.gz')
for i in r:
    for j in r[i]:
        print(i,j,len(r[i][j]))
        category = i+'-'+j
        for k in r[i][j]:
            data = r[i][j][k]
            hashvalue = getTextHashValues(data).tobytes()
            c.execute("insert into LMRD_1 values (?, ?, ?, ?)",  (category, k, data, hashvalue))


conn.commit()
conn.close()