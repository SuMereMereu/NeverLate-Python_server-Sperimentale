'''
Created on 04/mag/2015
@author: nicola, riccardo
'''
from flask import Flask , render_template, request, session, url_for, redirect, jsonify
from datetime import datetime, date, timedelta
from apiclient import discovery
from oauth2client import client
from os import urandom
import requests
import httplib2
import json

#GLOBAL VARIABLES

app = Flask(__name__)
app.secret_key=urandom(24)
urlScheduleTime = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_orario"
urlAPIpolito = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_elenco_materie"
All_user = {} 			#REMOVE WHEN DABASE IS ADDED



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
		list = []
		list.append(self.username, self.password, self.email, self.G_key, self.settings.system_status, self.settings.vibration_status, self.settings.sound_status, self.settings.delay, self.settings.default_settings)
		return list
		
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
		return list, self.uploaded
	
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



#HTML PAGES RENDERING

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():						#REMOVE WHEN DABASE IS ADDED
	if 'user' in session:
		return redirect (url_for('default_user'))
	else:
		return render_template('login.html', validation_login=request.args.get('valid'))

@app.route('/vision')
def vision():
    return render_template('vision.html')

@app.route('/requirements')
def requirements():
    return render_template('requirements.html')
    
@app.route('/registration', methods=['POST', 'GET'])
def registration():
	'''chiedo le credenziali qua cosi non faccio redirect nella pagina newuser'''
	if 'credentials' not in session:
		session['oauthcaller']='registration'												#CHECK FOR THE USER AUTHORIZATION
		return redirect(url_for('oauth2callback'))									#IF NOT PRESENT USER IS REDIRECTED 
		
																					#TO GOOGLE PAGE ASKING FOR PERMISSION
	credentials = client.OAuth2Credentials.from_json(session['credentials'])
		
	if credentials.access_token_expired:
		'''metto questo parametro in sessione per dire ad oauth dove ritornare'''
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
		return render_template('default_user.html',	vib=All_user[session['user']].settings.vibration_status,
													sound=All_user[session['user']].settings.sound_status,
													delay=All_user[session['user']].settings.delay,
													Gk=All_user[session['user']].G_key)
	else:
		return redirect(url_for('login'))

@app.route('/user/settings', methods=['POST', 'GET'])
def settings():
	if 'user' in session:
		return render_template('settings.html',	vib=All_user[session['user']].settings.vibration_status,
												sound=All_user[session['user']].settings.sound_status,
												delay=All_user[session['user']].settings.delay)
	else:
		return redirect(url_for('login'))

@app.route('/user/calendar', methods=['POST', 'GET'])
def calendar():
	if 'user' in session:
		return render_template('calendar.html', Gk=All_user[session['user']].G_key,
												search=request.args.get('search'))
	else:
		return redirect(url_for('login'))



#OPERATIVE URLS

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
	
	error=False
	mail=""
	psw=""
	usrname=""
	
	if (email == "" or email_rep == "" or email != email_rep):				#THE FOLLOWING 4 IF CONDION CHECK IF 										
		error = True														#THE FORM IS FILLED IN THE RIGHT WAY 
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
	
	if username in All_user:		#REMOVE WHEN DABASE IS ADDED			#IF THE USER ALREADY EXISTS THE NEW ONE IS ALERTED
		return redirect(url_for('login')+"?valid=extUsr")
	
	else:	
		calendar = {'summary': 'neverLate','timeZone': 'Europe/Rome'}					#NEVERLATE CALENDAR CREATION AND STORAGE 
																						#OF CALENDAR KEY
		created_calendar = service.calendars().insert(body=calendar).execute()
		temp.G_key=created_calendar['id']
			
		All_user[username]=temp				#REMOVE WHEN DABASE IS ADDED
		
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

@app.route('/loggining', methods=['POST', 'GET'])	#CREATION A SESSION FROM AN EXISTING USER
def loggining():
	global All_user				#REMOVE WHEN DABASE IS ADDED
	username=request.form.get('username')
	password=request.form.get('password')
	
	if username in All_user:											#CHECK FOR AN EXISTING USER, AND
		check=All_user[username]										#EVENTUALLY, IF USER'S PASSWORD IS CORRECT		
		if check.password == password:
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
					
		All_user[session['user']].settings.vibration_status=request.form.get('vibration')		
		All_user[session['user']].settings.sound_status=request.form.get('sound')
		All_user[session['user']].settings.delay=request.form.get('delay')
		All_user[session['user']].settings.default_settings="f"
		
		#STORE IN DATABASE NEW USER SETTINGS
		
		return redirect(url_for('settings'))
		
	else:
		return redirect(url_for('login')+"?valid=Exprd")
		
@app.route('/calendar_step1', methods=['POST', 'GET'])		#NEW SUBJECT SEARCH
def cal_step1():
	global urlAPIpolito
	global All_user
	
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
		if subject.uploaded == False:																		#EACH ELEMENT OF THE USER'S OFFICIAL SUBJECT LIST
			scheduleParameters = { 'listachiavimaterie': subject.code, 'datarif': str(date.today())}
			APIrequest = requests.post(urlScheduleTime, json=scheduleParameters)
			schedule = APIrequest.json()
			APIrequest.close()
			#ho spostato oneweekspan dentro l'if	
			if schedule['d']:
				OneWeekSpan= timedelta(7,0,0)+DateFormat(schedule['d'][0]['start'])
				for item in schedule['d']:
					if DateFormat(item['start']) < OneWeekSpan:
						event=PolitoCalendar()
						event=format_schedule(item['text'])
						event.start=item['start']
						event.end=item['end']
						G_cal_request= {"end":{"dateTime": event.end,"timeZone":"Europe/Rome"}, "start":{"dateTime": event.start,"timeZone":"Europe/Rome"}, "recurrence":["RRULE:FREQ=WEEKLY;UNTIL=20150631T170000Z"], "summary": event.subject+' '+event.professor, "description": event.comment, "location": event.classroom, "colorId":"3"}
						'''modifica calendarId=All_user[session[user]].Gkey'''
						created_event=service.events().insert(calendarId=All_user[session['user']].G_key, body=G_cal_request).execute()
						subject.uploaded=True
			else:
				pass
			
	del session['search_res']
	return redirect(url_for('calendar'))
	
@app.route('/logout')						#LOGOUT FUNCTION
def logout():
	del session['user']
	'''credo che serva'''
	if 'credentials' in session:
		del session['credentials']
	return redirect(url_for('index'))



#REST URL

@app.route('/get_pref/<username>', methods=['POST', 'GET'])
def get_pref(username):
	return jsonify(All_user[username].settings.settings_dict())


#MAIN

if __name__ == '__main__':
	user=User()
	user.username='Riccardo'
	user.password='Gavoi91'
	user.G_key='9p2jhrvdq00b2o8fp34lmurif4%40group.calendar.google.com'
	All_user[user.username]=user
	app.run(debug=True, host='0.0.0.0', threaded=True)
	pass
	