'''
Created on May 26, 2015

@author: federico
'''

import MySQLdb

def main():
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    query="DROP TABLE CHECKPOINTS,GRAPH,PLACES,MAC_ADDRESS"
    cursor.execute(query)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()