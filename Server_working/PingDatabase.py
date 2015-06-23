'''
Created on 23/giu/2015

@author: nicola
'''
import MySQLdb

#DATABASE FOR PING
def insertInProfUser(FullName,UserName,GCKey):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="INSERT INTO PROF_USER VALUES('%s','%s','%s')"%(UserName,FullName,GCKey)
    cursor.execute(query)
    conn.commit()
    conn.close()
    
def getIfUserIsPresent(FullName):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT * FROM PROF_USER WHERE FullName='%s'"%(FullName)
    cursor.execute(query)
    number=cursor.fetchone()
    conn.close()
    
    if number !=None:
        return True
    else:
        return False
    
def getGCalKeyProfessor(FullName):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT GoogleCalKey FROM PROF_USER WHERE FullName='%s'"%(FullName)
    
    cursor.execute(query)
    users=cursor.fetchall()
    for line in users:
        newline=" ".join(str(l) for l in line)
        
    conn.close()
    
    return newline

def insertInviteKey(GCalKey,ApiSubjectCode,lista):  
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    for InvKey in lista:
        query="INSERT INTO INVITES VALUES('%s','%s','%s')"%(GCalKey,ApiSubjectCode,InvKey)
        cursor.execute(query)
    conn.commit()
    
    conn.close() 
    
def getInviteKey(FullName,ApiSubjectCode):
    
    GoogleCalKey=getGCalKeyProfessor(FullName)

    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT InviteKey FROM INVITES WHERE GoogleCalKey='%s' AND ApiSubjectCode='%s'"%(GoogleCalKey,ApiSubjectCode)
    
    cursor.execute(query)
    invites=cursor.fetchall()
    invitelist=[]
    for line in invites:
        newline=" ".join(str(l) for l in line)
        invitelist.append(newline)
        
    conn.close()
    return invitelist    

def getUsersAttendACourse(courseCode):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT UserName FROM ATTENDANCE WHERE ApiSubjectCode='%s'"%(courseCode)
    
    cursor.execute(query)
    users=cursor.fetchall()
    for line in users:
        newline=" ".join(str(l) for l in line)
        newline=newline.split()
        
    conn.close()
    
    return newline

def getIfUploadedToCalendar(username):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    
    query="SELECT Uploaded FROM ATTENDANCE WHERE UserName='%s'"%(username)
    
    cursor.execute(query)
    uploaded=cursor.fetchall()
    for line in uploaded:
        newline=" ".join(str(l) for l in line)
        newline=newline.split()
        
    conn.close()
    return newline