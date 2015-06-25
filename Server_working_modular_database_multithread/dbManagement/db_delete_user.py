'''
Created on 07/giu/2015

@author: casa
'''
import MySQLdb

def main():
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    query="DROP TABLE ATTENDANCE,SUBJECTS,USERS,INVITES,PROF_USER"
    cursor.execute(query)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
