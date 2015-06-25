'''
Created on 23/giu/2015

@author: nicola
'''

import MySQLdb


#DATABASE FUNCTIONS

def insertUser(lista):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="INSERT INTO USERS VALUES('%s','%s','%s','%s','%s','%s','%s','%d')"%(lista[0],lista[1],lista[2],lista[3],lista[4],lista[5],lista[6],int(lista[7]))
    cursor.execute(query)
    conn.commit()
    conn.close()
    
def insertSubject(lista):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query='SELECT * FROM SUBJECTS WHERE ApiSubjectCode="%s"'%(lista[0])
    cursor.execute(query)
    num=cursor.fetchone()
    
    if num==None:
        query="INSERT INTO SUBJECTS VALUES('%s','%s','%s','%s')"%(lista[0],lista[1],lista[2],lista[3])
        cursor.execute(query)
    conn.commit()
    conn.close()
    
def insertAttendance(lista1,lista2,valore): 
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="INSERT INTO ATTENDANCE VALUES('%s','%s','%s)"%(lista1[0],lista2[0],valore)
    cursor.execute(query)
    conn.commit()
    conn.close()
    
def insertSettingsUser(lista):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    
    query="UPDATE USERS SET VibrationStatus='%s',SoundStatus='%s', DefaultValue='%s',Delay='%d'\
        WHERE UserName='%s'"%(lista[1],lista[2],lista[4],int(lista[3]),lista[0])
        
    cursor.execute(query)
    conn.commit()
    conn.close()
    
def insertNewGcalUser(newKey,username):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    
    query="UPDATE USERS SET GoogleCalKey='%s'\
        WHERE UserName='%s'"%(newKey,username)
        
    cursor.execute(query)
    conn.commit()
    conn.close()
    
def getUserSettings(username):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT GoogleCalKey,VibrationStatus,SoundStatus,DefaultValue,Delay FROM USERS WHERE UserName='%s'"%(username)
    cursor.execute(query)
    settings=cursor.fetchall()
    for line in settings:
        newline=" ".join(str(l) for l in line)
        newline=newline.split()
        
    conn.close()
    return newline

def getUser(username):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT UserName FROM USERS WHERE UserName='%s'"%(username)
    cursor.execute(query)
    settings=cursor.fetchone()
    conn.close()
    if settings!=None:
        return True
    else:
        return False
    
def getPass(username):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT Password FROM USERS WHERE UserName='%s'"%(username)
    
    cursor.execute(query)
    passw=cursor.fetchall()
    for line in passw:
        newline=" ".join(str(l) for l in line)
        newline=newline.split()
        
    conn.close()
    
    return newline[0]    