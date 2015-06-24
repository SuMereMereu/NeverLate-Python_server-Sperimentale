'''
Created on 23/giu/2015

@author: nicola
'''

import MySQLdb



#GRAPH

def updateDatabase(lista,Place1,Place2):
    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    '''acquisisco vecchio valore'''
    query="SELECT Time FROM GRAPH WHERE Place1='%s' AND Place2='%s'"%(Place1,Place2)
    cursor.execute(query)
    old=cursor.fetchall()
    for line in old:
        newline=" ".join(str(l) for l in line)
        newline=newline.split()
    old=newline[0]
    '''prendo la mediana?'''
    lista.sort()
    lung=len(lista)
    indice=lung/2
    new=lista[indice]
    '''faccio la media e update'''
    new=(float(new)+float(old))/2
    
    sleep(10)
    
    query="UPDATE GRAPH SET Time='%f' WHERE Place1='%s' AND Place2='%s'"%(new,Place1,Place2)
    cursor.execute(query)
    conn.commit()
    
    conn.close
    
def QUERY_RESULT_JSON(tablename):

    conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")
    cursor=conn.cursor()
    query="SELECT * FROM %s" %(tablename)
    
    cursor.execute(query)
    mac=cursor.fetchall()
    
    rowarray_list=""
    lista=[]
    diz={}
    
    for row in mac:
        rowarray_list=" ".join(str(l) for l in row)
        lista.append(rowarray_list)
        
    diz["value"]=json.dumps(lista)
    
    return diz