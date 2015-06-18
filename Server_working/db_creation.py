'''
Created on May 26, 2015

@author: federico
'''

import MySQLdb

def GRAPH_CREATION():
    
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query='CREATE TABLE IF NOT EXISTS GRAPH(Place1 VARCHAR(30),Place2 VARCHAR(30),TIME FLOAT(5),PRIMARY KEY(Place1,Place2),FOREIGN KEY(Place1) REFERENCES PLACES(Place),FOREIGN KEY(Place2) REFERENCES PLACES(Place));'

    cursor.execute(query)
    number=cursor.fetchone()
    
    if number ==None:
    
        f=open('Text_Files/GRAPH.dat',"r")
        strall=f.read()
        new=strall.split('\n')
        del new[-1]
    
        for line in new:
            line=line.split()
            query="INSERT INTO GRAPH VALUES('%s','%s','%f')"%(line[0],line[1],float(line[2]))
            cursor.execute(query)
        f.close()
        
    conn.commit()
    conn.close
    
    
    
def MAC_CREATION():
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    query='CREATE TABLE IF NOT EXISTS MAC_ADDRESS(Mac VARCHAR(17) PRIMARY KEY)'

    cursor.execute(query)
    number=cursor.fetchone()
    
    if number ==None:
    
        f=open('Text_Files/MAC.dat',"r")
        strall=f.read()
        new=strall.split('\n')
        del new[-1]
    
        for line in new:
            line=line.split()
            query="INSERT INTO MAC_ADDRESS VALUES('%s')"%(line[0])
            cursor.execute(query)
        f.close()
        
    conn.commit()  
    conn.close
    
    
    
def PLACES_CREATION():
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    query='CREATE TABLE IF NOT EXISTS PLACES(Place VARCHAR(30),Mac VARCHAR(17),Power TINYINT(4),PRIMARY KEY(Place,Mac))'

    cursor.execute(query)
    number=cursor.fetchone()
    
    if number ==None:
    
        f=open('Text_Files/PLACES.dat',"r")
        strall=f.read()
        new=strall.split('\n')
        del new[-1]
    
        for line in new:
            line=line.split()
            query="INSERT INTO PLACES VALUES('%s','%s','%d')"%(line[0],line[1],int(line[2]))
            cursor.execute(query)
        f.close()
    
    conn.commit()    
    conn.close
    
   
    
def CHECKPOINT_CREATION():
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    query='CREATE TABLE IF NOT EXISTS CHECKPOINTS(Checks VARCHAR(30) NOT NULL,Places VARCHAR(30) NOT NULL)'


    cursor.execute(query)
    number=cursor.fetchone()
    
    if number ==None:
    
        f=open('Text_Files/CHECK.dat',"r")
        strall=f.read()
        new=strall.split('\n')
        del new[-1]
    
        for line in new:
            line=line.split()
            query="INSERT INTO CHECKPOINTS VALUES('%s','%s')"%(line[0],line[1])
            cursor.execute(query)
        f.close()
    
    conn.commit()    
    conn.close
    
   
    
def USER_CREATION():  
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    
    query='CREATE TABLE IF NOT EXISTS USERS(UserName VARCHAR(20) PRIMARY KEY,Password VARCHAR(20)NOT NULL,\
            Mail VARCHAR(30) NOT NULL,GoogleCalKey VARCHAR(50) NOT NULL,VibrationStatus VARCHAR(5),\
            SoundStatus VARCHAR(5),DefaultValue VARCHAR(5),Delay TINYINT(4))'
    cursor.execute(query)
    
    
    query='CREATE TABLE IF NOT EXISTS SUBJECTS(ApiSubjectCode VARCHAR(50) PRIMARY KEY,Subject VARCHAR(20),Surname VARCHAR(4),Professor VARCHAR(15))'
    cursor.execute(query)

    
    query='CREATE TABLE IF NOT EXISTS ATTENDANCE(UserName VARCHAR(20),ApiSubjectCode VARCHAR(50),Uploaded VARCHAR(4),PRIMARY KEY(UserName,ApiSubjectCode),\
        FOREIGN KEY(UserName) REFERENCES USERS(UserName),FOREIGN KEY(ApiSubjectCode) REFERENCES SUBJECTS(ApiSubjectCode))'
    cursor.execute(query)
    
    
    conn.commit()
    conn.close
     
def main():
    MAC_CREATION()
    PLACES_CREATION()
    GRAPH_CREATION()
    CHECKPOINT_CREATION()
    USER_CREATION()
    
if __name__ == '__main__':
    main()
    