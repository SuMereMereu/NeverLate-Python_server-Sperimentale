'''
Created on 04/mag/2015
@author: nicola, riccardo, federico
'''
from flask import Flask , render_template, request, session, url_for, redirect, jsonify
from datetime import datetime, date, timedelta
from apiclient import discovery
from oauth2client import client
from os import urandom
from time import sleep
import requests
import httplib2
import json
import MySQLdb

#GLOBAL VARIABLES

app = Flask(__name__)
app.secret_key=urandom(24)
urlScheduleTime = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_orario"
urlAPIpolito = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_elenco_materie"
All_prof = {}
All_user = {} 			#REMOVE WHEN DABASE IS ADDED
nmax=2					#MAX ARCS TO UPLOAD CHANGE IT
diz={} 					#QUEUE FOR UPDATING TIMETRAVELS


#CLASSES

class Settings:
	def __init__(self):
		self.vibration_status = "on"
		self.sound_status = "on"
		self.delay = -5
		self.default_settings = "t"
	
	def settings_dict(self):
		dict={}
		dict['vib'] = self.vibration_status
		dict['snd'] = self.sound_status
		dict['delay'] = self.delay
		return dict
		
class User:
	def __init__(self):
		self.username = ""
		self.password = ""
		self.email = ""
		self.G_key = ""
		self.settings = Settings()
		self.subjects = []
			
	def User_Output_List(self):
		lista = []
		lista.append(self.username)
		lista.append(self.password)
		lista.append(self.email)
		lista.append(self.G_key)
		lista.append(self.settings.vibration_status)
		lista.append(self.settings.sound_status)
		lista.append(self.settings.default_settings)
		lista.append(self.settings.delay)
		print lista
		return lista
		
class PolitoRequest:
	def __init__(self, materia, alfabetica, docente, codice):
		self.subject = materia
		self.alphabetic = alfabetica
		self.prof = docente
		self.code = codice
		self.uploaded = False
		
	def Subj_Output_List(self):				#@FEDERICO, MULTIPLE RETURN
		list = []
		list.append(self.code, self.subject, self.alphabetic, self.prof)
		return list
	
	def Subj_Output_Uploaded(self):#FOR ATTENDANCE TEABLE
		return self.uploaded
	
	
	def dict_for_session(self):
		dict={}
		dict['subj']= self.subject
		dict['alpha']= self.alphabetic
		dict['prof']= self.prof
		dict['code']= self.code
		dict['upl']= self.uploaded
		return dict
	
	def page_string(self):
		return self.subject+", "+self.alphabetic+", "+self.prof+", quadrimestre # "+self.code[9]
		
class PolitoCalendar:
	def __init__(self, subject="", comment="", professor="", classroom=""):
		self.start = ""
		self.end = ""
		self.subject = subject
		self.comment = comment
		self.professor = professor
		self.classroom = classroom
		
class Professor:
	def __init__(self, username, password, mail):
		self.G_key = ""
		self.username = username
		self.password = password
		self.mail = mail 
		self.subjects = []#Subjects if for memorizing what subjects are already in memory
		self.inviteKeys={} 
#ASSOCIATION DICTIONARY: GIVES THE ASSOCIATION BETWEEN A PROF NAME OF THE POLITO CALENDAR
#API AND ITS USERNAME

Association={}	
		
		
#GLOBAL FUNCTIONS
		
def DateFormat(datarfc):
    datavect=datarfc.split('T')[0].split('-')
    data=date(int(datavect[0]),int(datavect[1]),int(datavect[2]))
    return data

def format_schedule(item_text):
    
    textformatted=item_text.replace('<p style="margin:0"></p>',"")
    textformatted=textformatted.replace('</p>',"*")
    textformatted=textformatted.replace('<p style="margin:0">',"*")
    textformatted=textformatted.replace('**',"*")
    '''modifica  textformatted=textformatted.split('*')'''
    textformatted=textformatted.split('*')
    
    if len(textformatted) == 5:
        result = PolitoCalendar(textformatted[0],textformatted[1],textformatted[2],textformatted[3])
        return result
    else:
        result = PolitoCalendar(textformatted[0],"",textformatted[1],textformatted[2])
        return result



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
	settings=cursor.fetchall()
	conn.close()
	if settings!=None:
		return True
	else:
		return False	
	

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



#HTML PAGES RENDERING

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
	if 'prof' in session:
		return redirect (url_for('default_professor'))						
	if 'user' in session:
		return redirect (url_for('default_user'))
	else:
		return render_template('login.html', validation_login=request.args.get('valid'))

@app.route('/prof_login')
def prof_login():
	if 'user' in session:
		return redirect (url_for('default_user'))						
	if 'prof' in session:
		return redirect (url_for('default_professor'))
	else:
		return render_template('prof_login.html', validation_login=request.args.get('valid'))
		
@app.route('/vision')
def vision():
    return render_template('vision.html')

@app.route('/requirements')
def requirements():
    return render_template('requirements.html')
    
@app.route('/registration', methods=['POST', 'GET'])
def registration():
	if 'credentials' not in session:
		session['oauthcaller']='registration'										#CHECK FOR THE USER AUTHORIZATION
		return redirect(url_for('oauth2callback'))									#IF NOT PRESENT USER IS REDIRECTED 
		
																					#TO GOOGLE PAGE ASKING FOR PERMISSION
	credentials = client.OAuth2Credentials.from_json(session['credentials'])
		
	if credentials.access_token_expired:
		session['oauthcaller']='registration'
		return redirect(url_for('oauth2callback'))	
		
	return render_template('registration.html', error=request.args.get('error'),
												mail=request.args.get('mail'),
												psw=request.args.get('psw'),
												usrname=request.args.get('usrname'))

@app.route('/architecture')
def architecture():
	return render_template('architecture.html')
	
@app.route('/user/first', methods=['POST', 'GET'])
def default_user():
	if 'user' in session:
		lista=getUserSettings(session['user'])
		
		return render_template('default_user.html',	vib=lista[1],
													sound=lista[2],
													delay=lista[4],
													Gk=lista[0])
	else:
		return redirect(url_for('login'))

@app.route('/user/settings', methods=['POST', 'GET'])
def settings():
	if 'user' in session:
		lista=getUserSettings(session['user'])
		return render_template('settings.html',	vib=lista[1],
												sound=lista[2],
												delay=lista[4])
	else:
		return redirect(url_for('login'))

@app.route('/user/calendar', methods=['POST', 'GET'])
def calendar():
	if 'user' in session:
		lista=getUserSettings(session['user'])
		return render_template('calendar.html', Gk=lista[0],
												search=request.args.get('search'))
	else:
		return redirect(url_for('login'))



#GENERAL OPERATIVE URLS

@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
	if 'user' in session:
		return redirect(url_for('login'))
	
	credentials = client.OAuth2Credentials.from_json(session['credentials'])

	http_auth = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http_auth)
	
	email=request.form.get('email')							#COLLECTING DATA FROM FORM IN REGISTRATION PAGE
	email_rep=request.form.get('email_rep')
	password=request.form.get('password')
	password_rep=request.form.get('password_rep')
	username=request.form.get('username')
	prof_checkbox=request.form.get('prof_checkbox')
	
	error=False
	mail=""
	psw=""
	usrname=""
	
	if (email == "" or email_rep == "" or email != email_rep):				#THE FOLLOWING 4 IF CONDION CHECK IF 										
		error = True																					#THE FORM IS FILLED IN THE RIGHT WAY 
		mail='mail=f'
	
	if (password == "" or password_rep == "" or password != password_rep):
		error = True
		psw='psw=f'
	
	if (username == ""):
		error = True
		usrname='usrname=f'
	
	if error == True:
		return redirect(url_for('registration')+"?error=t&"+mail+"&"+psw+"&"+usrname)
	
	
	if prof_checkbox == 'on':
		temp = Professor (username, password, email)
		
		if username in All_prof:		#REMOVE WHEN DABASE IS ADDED			#IF THE USER ALREADY EXISTS THE NEW ONE IS ALERTED
			return redirect(url_for('prof_login')+"?valid=extUsr")
			
		else:	
			calendar = {'summary': 'neverLate','timeZone': 'Europe/Rome'}					#NEVERLATE CALENDAR CREATION AND STORAGE 
																						#OF CALENDAR KEY
			created_calendar = service.calendars().insert(body=calendar).execute()
			temp.G_key=created_calendar['id']
		
		
			insertUser(temp.User_Output_List())
			All_prof[username]=temp				#REMOVE WHEN DABASE IS ADDED
		
			return redirect(url_for('prof_login'))
		
	else:
		
		temp=User()
		temp.username=username				
		temp.password=password
		temp.email=email
		
		if username in All_user:		#REMOVE WHEN DABASE IS ADDED			#IF THE USER ALREADY EXISTS THE NEW ONE IS ALERTED
			return redirect(url_for('login')+"?valid=extUsr")
	
		else:	
			calendar = {'summary': 'neverLate','timeZone': 'Europe/Rome'}					#NEVERLATE CALENDAR CREATION AND STORAGE 
																						#OF CALENDAR KEY
			created_calendar = service.calendars().insert(body=calendar).execute()
			temp.G_key=created_calendar['id']
		
		
		
			'''All_user[username]=temp'''				
			insertUser(temp.User_Output_List())			#INSERTION IN DATABASE 'USERS'
		
			return redirect(url_for('login'))

@app.route('/oauth2callback')		#GOOGLE CALENDAR PAGE ASKING FOR USER AUTHORIZATION, STANDARD FUNCTION
def oauth2callback():
	var=request.args.get('var')
	flow = client.flow_from_clientsecrets('client_secrets.json',
        								  scope='https://www.googleapis.com/auth/calendar',
        								  redirect_uri=url_for('oauth2callback', _external=True))
	
	if 'code' not in request.args:
    		auth_uri=flow.step1_get_authorize_url()
     		return redirect(auth_uri)
	else:
        	auth_code = request.args.get('code')
         	credentials = flow.step2_exchange(auth_code)
          	session['credentials'] = credentials.to_json()
          	'''dico a dove fare le redirect'''
          	redirectString=session['oauthcaller']
          	del session['oauthcaller']
           	return redirect(url_for(redirectString))
           	
@app.route('/logout')						#LOGOUT FUNCTION
def logout():
	if 'user' in session:
		del session['user']
		
	if 'prof' in session:
		del session['prof']
		
	if 'credentials' in session:
		del session['credentials']
	return redirect(url_for('index'))



#OPERATIVE URLS STUDENTS
#WORK!
@app.route('/loggining', methods=['POST', 'GET'])	#CREATION A SESSION FROM AN EXISTING USER
def loggining():
	global All_user				#REMOVE WHEN DABASE IS ADDED
	username=request.form.get('username')
	password=request.form.get('password')
	
	if getUser(username):		#CHECK FOR AN EXISTING USER, AND	
		print getPass(username)						#EVENTUALLY, IF USER'S PASSWORD IS CORRECT		
		if password==getPass(username):
			session['user']=username
													 
			return redirect( url_for('default_user'))		
		
		else:
			return redirect(url_for('login')+"?valid=PswF")
	else:
		if username == "":
			return redirect(url_for('login')+"?valid=NoUsr")
			
		else:
			return redirect(url_for('login')+"?valid=UsrF")				
	
@app.route('/G_key_mod', methods=['POST', 'GET'])	#GOOGLE CALENDAR KEY MODIFICATION
def Gkeymod():
	global All_user
	if not 'user' in session:
		return redirect(url_for('login')+"?valid=Exprd")
	
	All_user[session['user']].G_key=request.form.get('G_key')
	
	
	
	#INTERACTION WITH DATABASE, SEND UPDATED USER
	
	return redirect(url_for('default_user'))
	
@app.route('/settings_definition', methods=['POST', 'GET']) #PERSONAL SETTINGS CUSTOMIZATION
def settings_def():
	global All_user
	if 'user' in session:
		lista=[]
		lista.append(session['user'])
		lista.append(request.form.get('vibration'))		
		lista.append(request.form.get('sound'))
		lista.append(request.form.get('delay'))
		lista.append("f")
		
		insertSettingsUser(lista) 			#ADDING USER SETTINGS TO DATABASE
		
		return redirect(url_for('settings'))
		
	else:
		return redirect(url_for('login')+"?valid=Exprd")
		
@app.route('/calendar_step1', methods=['POST', 'GET'])		#NEW SUBJECT SEARCH
def cal_step1():
	global urlAPIpolito
	
	if not 'user' in session:
		return redirect(url_for('login')+"?valid=Exprd")
	
	search=""
	
	session['search_res']=[]
	search=request.form.get('search')
	
	if search == "":
		del session['search_res']
		return redirect(url_for('calendar'))
	
	APIrequest = requests.post(urlAPIpolito, json= { 'txt': search })		#COMUNICATION WITH POLITO API
	
	received=APIrequest.json()
	
	APIrequest.close()
	
	temp=[]						
	
	if received['d']:						#CONDITION CHECKING ELEMENTS ON RESPONSE LIST															
		for element in received['d']:
			temp_obj=PolitoRequest(element['materia'], element['alfabetica'], element['docente'], element['chiave'])	#IMPORTING RESPONSE ELEMENTS
			temp.append(temp_obj)	   			#LOCAL STORAGE OF RESPONSE ELEMENTS		
	
	if temp:						#CHECK OF LOCAL DATA (IF PRESENT OR NOT)
		for subject in temp:
			flag=True
			''' qua midava errore quando provavo a inserire una seconda materia ho fatto il ciclo col break'''
			for personal_subj in All_user[session['user']].subjects:			#ONLY THE SUBJECTS NOT IN THE USER'S PERSONAL DATA ARE STORED TEMPORARLY 
				if subject.code == personal_subj.code:									#IN THE DATABASE
					flag = False
					break
			if flag:
				session['search_res'].append(subject.dict_for_session())
			
		if not session['search_res']:
			return redirect(url_for('calendar')+"?select=empty")
		
		else:
			return redirect(url_for('calendar')+"?search="+search)
			
	else:
		return redirect(url_for('calendar')+"?select=empty")
		
@app.route('/calendar_step2', methods=['POST', 'GET'])		#NEW SUBJECT ADDITION
def cal_step2():
	global All_user
	temp=request.form.get('subjects')
																							#TO GOOGLE PAGE ASKING FOR PERMISSION	
	
	
	if 'credentials' not in session:
		session['oauthcaller']='cal_step2'																				#CHECK FOR THE USER AUTHORIZATION
		return redirect(url_for('oauth2callback'))								#IF NOT PRESENT USER IS REDIRECTED
	
	credentials = client.OAuth2Credentials.from_json(session['credentials'])
		
	if credentials.access_token_expired:
		session['oauthcaller']='cal_step2'	
		return redirect(url_for('oauth2callback'))
			
	else:
		http_auth = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http_auth)
	
	exit = True
	
	for subject in session['search_res']:
		control=subject['subj']+", "+subject['alpha']+", "+subject['prof']+", quadrimestre # "+subject['code'][9]
		if control == temp and exit:										#IF THERE IS A MATCH BETWEEN THE SELECTED ITEM AND ANY ELEMENT IN THE TEMPORARLY SUBJECT LIST
			dict_to_obj=PolitoRequest(subject['subj'], subject['alpha'], subject['prof'], subject['code'])
			dict_to_obj.uploaded = False		  
			All_user[session['user']].subjects.append(dict_to_obj)			#TROVARE SOLUZIONE PER CARICARE OGGETTO, STORED IN DATABASE, THE SUBJECT IS ADDED IN THE USER'S OFFICIAL SUBJECT LIST
			exit = False
	
	for subject in All_user[session['user']].subjects:														#SYNCRONIZATION WITH GOOGLE CALENDAR IS CHECKED FOR 
		if subject.uploaded == False:
			if subject.professor in All_prof:#Pingable subject
				if subject.code in All_prof[subject.professor].inviteKeys:
					for inviteKey in All_prof[subject.professor].inviteKeys:
						event = service.events().get(calendarId=All_prof[subject.professor].G_key, eventId=inviteKey).execute()
						attendeeList=event["attendees"]
						attendee={}
    					attendee['email']=All_user[session['user']].G_key
    					attendeeList.append(attendee)
    					updated_event = service.events().update(calendarId=All_prof[subject.professor], eventId=inviteKey, body=event).execute()
			else:#NON PINGABLE SUBJECT
																					#EACH ELEMENT OF THE USER'S OFFICIAL SUBJECT LIST
				scheduleParameters = { 'listachiavimaterie': subject.code, 'datarif': str(date(2015,5,29))}
				APIrequest = requests.post(urlScheduleTime, json=scheduleParameters)
				schedule = APIrequest.json()
				APIrequest.close()	
				if schedule['d']:
					OneWeekSpan= timedelta(7,0,0)+DateFormat(schedule['d'][0]['start'])
					for item in schedule['d']:
						if DateFormat(item['start']) < OneWeekSpan:
							event=PolitoCalendar()
							event=format_schedule(item['text'])
							event.start=item['start']
							event.end=item['end']
							G_cal_request= {"end":{"dateTime": event.end,"timeZone":"Europe/Rome"}, "start":{"dateTime": event.start,"timeZone":"Europe/Rome"}, "recurrence":["RRULE:FREQ=WEEKLY;UNTIL=20150631T170000Z"], "summary": event.subject, "description": event.comment+' '+event.professor, "location": event.classroom, "colorId":"3"}
							'''modifica calendarId=All_user[session[user]].Gkey'''
							created_event=service.events().insert(calendarId=All_user[session['user']].G_key, body=G_cal_request).execute()
							subject.uploaded=True
				else:
					pass
			
	del session['search_res']
	return redirect(url_for('calendar'))


	
#OPERATIVE URLS PROFESSORS

@app.route('/prof_loggining')
def prof_loggining():
	global All_prof				#REMOVE WHEN DABASE IS ADDED
	username=request.form.get('username')
	password=request.form.get('password')
	
	if username in All_prof:											#CHECK FOR AN EXISTING USER, AND
		check=All_prof[username]										#EVENTUALLY, IF USER'S PASSWORD IS CORRECT		
		if check.password == password:
			session['prof']=username
			
											 
			return redirect( url_for('default_professor'))		
		
		else:
			return redirect(url_for('prof_login')+"?valid=PswF")
	else:
		if username == "":
			return redirect(url_for('prof_login')+"?valid=NoUsr")
			
		else:
			return redirect(url_for('prof_login')+"?valid=UsrF")



#REST URL

@app.route('/get_pref/<username>', methods=['POST', 'GET'])
def get_pref(username):
	return jsonify(All_user[username].settings.settings_dict())



#GRAPH ROUTES

@app.route("/updatedb/<key>") 
def getquery(key):
	query=key.replace("-", " ").encode("ascii","ignore")

	query=query.split()
	'''inserisco nel dizionario'''
	diz[query[0]+query[1]].append(query[2])
	if(len(diz[query[0]+query[1]])>nmax):
		'''lancio processo di update'''
		pu=Process(target=updateDatabase,args=(diz[query[0]+query[1]],query[0],query[1],))
		pu.start()
		'''svuoto la coda'''
		del diz[query[0]+query[1]][:]
		
	return 'OK',200

@app.route("/getdb")  
def getdb():
	
	MAC=QUERY_RESULT_JSON("MAC_ADDRESS")
	PLACES=QUERY_RESULT_JSON("PLACES")
	GRAPH=QUERY_RESULT_JSON("GRAPH")
	CHECK=QUERY_RESULT_JSON("CHECKPOINTS")
	
	vocabolario={}
	vocabolario["mac_address"]=MAC
	vocabolario["places"]=PLACES
	vocabolario["graph"]=GRAPH
	vocabolario["checkpoint"]=CHECK
	
	return jsonify(vocabolario)

@app.route("/getupdate")
def getdbupdate():
	
	GRAPH=QUERY_RESULT_JSON("GRAPH")
	vocabolario={}
	vocabolario["graph"]=GRAPH
	
	return jsonify(vocabolario)

@app.route("/getsettings/<username>")
def getUserSettingsJson(username):
	
	rowarray_list=getUserSettings(username)
	vocabolario={}
	vocabolario["settings"]=rowarray_list
	return jsonify(vocabolario)



#MAIN

if __name__ == '__main__':
	user=User()																	#FOR TESTING PURPOSE
	user.username='Riccardo'
	user.password='Gavoi91'
	user.G_key='9p2jhrvdq00b2o8fp34lmurif4%40group.calendar.google.com'
	All_user[user.username]=user
	
	conn=MySQLdb.connect(user='root',passwd="forzatoro",db="NeverLate")			#OPENING CONNECTION TO DATABASE
	cursor=conn.cursor()
	
	query="SELECT * FROM GRAPH"
	cursor.execute(query)
	response=cursor.fetchall()
	
	for line in response:									#DICTIONARY INIT
		newline=" ".join(str(l) for l in line)
		newline=newline.split()
		diz[newline[0]+newline[1]]=list()
	conn.close
	
	app.run(debug=True, host='0.0.0.0', threaded=True)
	pass
	