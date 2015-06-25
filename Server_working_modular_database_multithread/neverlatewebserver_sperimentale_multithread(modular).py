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
from multiprocessing import Process



#OUR MODULES
from UserDatabase import insertUser, insertSettingsUser, insertNewGcalUser, getUserSettings, getUser, getPass
from UserClasses import Settings, User, PolitoRequest, PolitoCalendar
from PingDatabase import insertInProfUser, getIfUserIsPresent, getGCalKeyProfessor, insertInviteKey, getInviteKey
from GraphDatabase import updateDatabase, QUERY_RESULT_JSON



#GLOBAL VARIABLES

app = Flask(__name__)
app.secret_key=urandom(24)
urlScheduleTime = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_orario"
urlAPIpolito = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_elenco_materie"
All_user = {} 			
nmax=3					#MAX ARCS TO UPLOAD CHANGE IT
diz={} 					#QUEUE FOR UPDATING TIMETRAVELS



#GLOBAL FUNCTIONS
		
def DateFormat(datarfc):
    datavect=datarfc.split('T')[0].split('-')
    data=date(int(datavect[0]),int(datavect[1]),int(datavect[2]))
    return data



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
	elif 'prof' in session:
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
	
@app.route('/professor/first', methods=['POST', 'GET'])
def default_professor():
	if 'prof' in session:
		lista=getUserSettings(session['prof'])
		
		return render_template('default_professor.html',	vib=lista[1],
													sound=lista[2],
													delay=lista[4],
													Gk=lista[0])
	else:
		return redirect(url_for('prof_login'))

@app.route('/user/settings', methods=['POST', 'GET'])
def settings():
	if 'user' in session:
		lista=getUserSettings(session['user'])
		return render_template('settings.html',	vib=lista[1],
												sound=lista[2],
												delay=lista[4])
	else:
		return redirect(url_for('login'))

@app.route('/professor/settings', methods=['POST', 'GET'])
def prof_settings():
	if 'prof' in session:
		lista=getUserSettings(session['prof'])
		return render_template('prof_settings.html',	vib=lista[1],
												sound=lista[2],
												delay=lista[4])
	else:
		return redirect(url_for('prof_login'))

@app.route('/user/calendar', methods=['POST', 'GET'])
def calendar():
	if 'user' in session:
		lista=getUserSettings(session['user'])
		session['Gkey']=lista[0]
		return render_template('calendar.html', Gk=lista[0],
												search=request.args.get('search'))
	else:
		return redirect(url_for('login'))

@app.route('/professor/calendar', methods=['POST', 'GET'])
def prof_calendar():
	if 'prof' in session:
		lista=getUserSettings(session['prof'])
		session['Gkey']=lista[0]
		return render_template('prof_calendar.html', Gk=lista[0],
												search=request.args.get('search'))
	else:
		return redirect(url_for('prof_login'))



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
	temp=User()
	temp.username=username				
	temp.password=password
	temp.email=email
		
	if getUser(username):			#IF THE USER ALREADY EXISTS THE NEW ONE IS ALERTED
		if prof_checkbox == 'on':					
			return redirect(url_for('prof_login')+"?valid=extUsr")
		else:	
			return redirect(url_for('login')+"?valid=extUsr")
	
	else:	
		calendar = {'summary': 'neverLate','timeZone': 'Europe/Rome'}					#NEVERLATE CALENDAR CREATION AND STORAGE 
																						#OF CALENDAR KEY
		created_calendar = service.calendars().insert(body=calendar).execute()
		temp.G_key=created_calendar['id']
					
		insertUser(temp.User_Output_List())			#INSERTION IN DATABASE 'USERS'
		if prof_checkbox == 'on':					#PROF AND USER ARE IN THE SAME DATABASE BUT ACCES DIFFERENT PAGES
			return redirect(url_for('prof_login'))
		else:	
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
          	
          	redirectString=session['oauthcaller'] #TELLS TO OAUTH WHERE TO REDIRECT
          	del session['oauthcaller']
           	return redirect(url_for(redirectString))
           	
@app.route('/logout')						#LOGOUT FUNCTION
def logout():
	if 'user' in session:
		del session['user']
	if 'Gkey' in session:
		del session['Gkey']
	if 'prof' in session:
		del session['prof']
	if 'credentials' in session:
		del session['credentials']
	if 'temp' in session:
		del session['temp']
	return redirect(url_for('index'))



#OPERATIVE URLS STUDENTS

@app.route('/loggining', methods=['POST', 'GET'])	#CREATION A SESSION FROM AN EXISTING USER
def loggining():
	global All_user				#REMOVE WHEN DABASE IS ADDED
	username=request.form.get('username')
	password=request.form.get('password')
	
	if getUser(username):		#CHECK FOR AN EXISTING USER, AND	
								#EVENTUALLY, IF USER'S PASSWORD IS CORRECT		
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
	NewKey=request.form.get('G_key')
	insertNewGcalUser(NewKey,session['user'])
	
	
	
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
	global All_user
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
			
			if  session['user'] not in All_user:
				All_user[session['user']]=[]
			for personal_subj in All_user[session['user']]:			#ONLY THE SUBJECTS NOT IN THE USER'S PERSONAL DATA ARE STORED TEMPORARLY 
				if subject.code == personal_subj.code:									
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
	if 'temp' not in session:
		session['temp']=request.form.get('subjects')
	
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
	
	print "******************************************************* HERE TEMP *******************************************************"
	temp = session['temp']
	print temp
	del session['temp']
	for subject in session['search_res']:
		control=subject['subj']+", "+subject['alpha']+", "+subject['prof']+", quadrimestre # "+subject['code'][9]
		if control == temp and exit:										#IF THERE IS A MATCH BETWEEN THE SELECTED ITEM AND ANY ELEMENT IN THE TEMPORARLY SUBJECT LIST
			dict_to_obj=PolitoRequest(subject['subj'], subject['alpha'], subject['prof'], subject['code'])
			dict_to_obj.uploaded = False		  
			All_user[session['user']].append(dict_to_obj)			#TROVARE SOLUZIONE PER CARICARE OGGETTO, STORED IN DATABASE, THE SUBJECT IS ADDED IN THE USER'S OFFICIAL SUBJECT LIST
			exit = False
	
	for subject in All_user[session['user']]:														#SYNCRONIZATION WITH GOOGLE CALENDAR IS CHECKED FOR
		print  
		if subject.uploaded == False:
			if getIfUserIsPresent(subject.prof):
				ProfGCal=getGCalKeyProfessor(subject.prof)
				inviteKeys=getInviteKey(subject.prof, subject.code)
				for inviteKey in inviteKeys:#AUTOINVITATION
					event = service.events().get(calendarId=ProfGCal, eventId=inviteKey).execute()
					if 'attendees' in event:#AUTOINVITATION AFTER OTHER STUDENTS
						attendeeList=event["attendees"]
						attendee={}
						attendee['email']=session['Gkey']
						attendeeList.append(attendee)
						event["attendees"]=attendeeList
						updated_event = service.events().update(calendarId=ProfGCal, eventId=inviteKey, body=event).execute()
					else:#FIRST AUTOINVITATION
						attendeeList=[]
						attendee={}
						attendee['email']=session['Gkey']
						attendeeList.append(attendee)
						event["attendees"]=attendeeList
						updated_event = service.events().update(calendarId=ProfGCal, eventId=inviteKey, body=event).execute()
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
							#event=format_schedule(item['text'])
							event.start=item['start']
							event.end=item['end']
							event.professor=item['nominativo_docente']
							event.comment=item['desc_evento']
							event.subject=item['titolo_materia']
							event.classroom='Aula'+item['aula']
							#event.classroom=item['aula']#Note instead of Aula 4D says 4D
							
							G_cal_request= {"end":{"dateTime": event.end,"timeZone":"Europe/Rome"}, "start":{"dateTime": event.start,"timeZone":"Europe/Rome"}, "recurrence":["RRULE:FREQ=WEEKLY;UNTIL=20150631T170000Z"], "summary": event.subject, "description": event.comment+' '+event.professor, "location": event.classroom, "colorId":"3"}
							created_event=service.events().insert(calendarId=session['Gkey'], body=G_cal_request).execute()
							subject.uploaded=True
				else:
					pass
			
	del session['search_res']
	del session['Gkey']
	return redirect(url_for('calendar'))


	
#OPERATIVE URLS PROFESSORS

@app.route('/prof_loggining',methods=['POST', 'GET'])
def prof_loggining():
	username=request.form.get('username')
	password=request.form.get('password')
	
	if getUser(username):		#CHECK FOR AN EXISTING USER, AND	
								#EVENTUALLY, IF USER'S PASSWORD IS CORRECT		
		if password==getPass(username):
			session['prof']=username
			
											 
			return redirect( url_for('default_professor'))		
		
		else:
			return redirect(url_for('prof_login')+"?valid=PswF")
	else:
		if username == "":
			return redirect(url_for('prof_login')+"?valid=NoUsr")
			
		else:
			return redirect(url_for('prof_login')+"?valid=UsrF")

@app.route('/prof_settings_definition', methods=['POST', 'GET']) #PERSONAL SETTINGS CUSTOMIZATION
def prof_settings_def():
	if 'prof' in session:
		lista=[]
		lista.append(session['prof'])
		lista.append(request.form.get('vibration'))		
		lista.append(request.form.get('sound'))
		lista.append(request.form.get('delay'))
		lista.append("f")
		
		insertSettingsUser(lista) 			#ADDING USER SETTINGS TO DATABASE
		
		return redirect(url_for('prof_settings'))
		
	else:
		return redirect(url_for('prof_login')+"?valid=Exprd")

@app.route('/prof_calendar_step1', methods=['POST', 'GET'])		#NEW SUBJECT SEARCH
def prof_cal_step1():
	global urlAPIpolito
	
	if not 'prof' in session:
		return redirect(url_for('prof_login')+"?valid=Exprd")
	
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
			
			if  session['prof'] not in All_user:
				All_user[session['prof']]=[]
			for personal_subj in All_user[session['prof']]:			#ONLY THE SUBJECTS NOT IN THE USER'S PERSONAL DATA ARE STORED TEMPORARLY 
				if subject.code == personal_subj.code:									
					flag = False
					break
			if flag:
				session['search_res'].append(subject.dict_for_session())
			
		if not session['search_res']:
			return redirect(url_for('prof_calendar')+"?select=empty")
		
		else:
			return redirect(url_for('prof_calendar')+"?search="+search)
			
	else:
		return redirect(url_for('prof_calendar')+"?select=empty")

@app.route('/prof_calendar_step2', methods=['POST', 'GET'])		#NEW SUBJECT ADDITION
def prof_cal_step2():
	global All_user
	if 'temp' not in session:
		session['temp']=request.form.get('prof_subjects')
		print "******************************************************* HERE TEMP 1 *******************************************************"
		print session['temp']
																							#TO GOOGLE PAGE ASKING FOR PERMISSION	
	
	if 'credentials' not in session:
		session['oauthcaller']='prof_cal_step2'																				#CHECK FOR THE USER AUTHORIZATION
		return redirect(url_for('oauth2callback'))								#IF NOT PRESENT USER IS REDIRECTED
	
	credentials = client.OAuth2Credentials.from_json(session['credentials'])
		
	if credentials.access_token_expired:
		session['oauthcaller']='prof_cal_step2'	
		return redirect(url_for('oauth2callback'))
			
	else:
		http_auth = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http_auth)
	
	exit = True
	
	print "******************************************************* HERE TEMP 2 *******************************************************"
	temp = session['temp']
	print temp
	del session['temp']
	for subject in session['search_res']:
		control=subject['subj']+", "+subject['alpha']+", "+subject['prof']+", quadrimestre # "+subject['code'][9]
		if control == temp and exit:
													#IF THERE IS A MATCH BETWEEN THE SELECTED ITEM AND ANY ELEMENT IN THE TEMPORARLY SUBJECT LIST
			dict_to_obj=PolitoRequest(subject['subj'], subject['alpha'], subject['prof'], subject['code'])
			dict_to_obj.uploaded = False		  
			All_user[session['prof']].append(dict_to_obj)			#TROVARE SOLUZIONE PER CARICARE OGGETTO, STORED IN DATABASE, THE SUBJECT IS ADDED IN THE USER'S OFFICIAL SUBJECT LIST
			print "%s"%(getIfUserIsPresent(subject['prof']))
			if not getIfUserIsPresent(subject['prof']):
				insertInProfUser(subject['prof'], session['prof'], session['Gkey'])
			exit = False
	
	for subject in All_user[session['prof']]:														#SYNCRONIZATION WITH GOOGLE CALENDAR IS CHECKED FOR 
		if subject.uploaded == False:																#EACH ELEMENT OF THE USER'S OFFICIAL SUBJECT LIST
			scheduleParameters = { 'listachiavimaterie': subject.code, 'datarif': str(date(2015,5,29))}
			APIrequest = requests.post(urlScheduleTime, json=scheduleParameters)
			schedule = APIrequest.json()
			APIrequest.close()	
			if schedule['d']:
				OneWeekSpan= timedelta(7,0,0)+DateFormat(schedule['d'][0]['start'])
				listEventKeys=[]
				for item in schedule['d']:
					if DateFormat(item['start']) < OneWeekSpan:
						event=PolitoCalendar()
						
						event.start=item['start']
						event.end=item['end']
						event.professor=item['nominativo_docente']
						event.comment=item['desc_evento']
						event.subject=item['titolo_materia']
						event.classroom='Aula'+item['aula']						
						G_cal_request= {"end":{"dateTime": event.end,"timeZone":"Europe/Rome"}, "start":{"dateTime": event.start,"timeZone":"Europe/Rome"}, "recurrence":["RRULE:FREQ=WEEKLY;UNTIL=20150631T170000Z"], "summary": event.subject, "description": event.comment+' '+event.professor, "location": event.classroom, "colorId":"3","anyoneCanAddSelf": "true", "attendees":[]}

						created_event=service.events().insert(calendarId=session['Gkey'], body=G_cal_request).execute()
						listEventKeys.append(created_event['id'])
						subject.uploaded=True
				insertInviteKey(session['Gkey'], subject.code, listEventKeys)
			else:
				pass
			
	del session['search_res']
	del session['Gkey']
	return redirect(url_for('prof_calendar'))



#REST URLS

@app.route("/updatedb/<key>") 
def getquery(key):
	query=key.replace("-", " ").encode("ascii","ignore")

	query=query.split()
	query2=[]
	query2.append(query[0])
	query2.append(query[1])
	query2.sort()
	
	'''inserisco nel dizionario'''
	diz[query2[0]+query2[1]].append(query[2])
	if(len(diz[query2[0]+query2[1]])>nmax):
		'''lancio processo di update'''
		pu=Process(target=updateDatabase,args=(diz[query2[0]+query2[1]],query2[0],query2[1],))
		pu.start()
		'''svuoto la coda'''
		del diz[query2[0]+query2[1]][:]
		
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
	
