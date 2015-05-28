'''
Created on 04/mag/2015
@author: nicola, riccardo
'''
from flask import Flask , render_template, request, session, url_for, redirect
from datetime import datetime, date, timedelta
from apiclient import discovery
from oauth2client import client
import json
import requests
import httplib2



#GLOBAL VARIABLES

app = Flask(__name__)
app.secret_key='chiavesegreta'
urlScheduleTime = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_orario"
urlAPIpolito = "http://www.swas.polito.it/dotnet/orari_lezione_pub/mobile/ws_orari_mobile.asmx/get_elenco_materie"
All_user = {} 



#CLASSES

class Settings:
	def __init__(self):
		self.system_status = "on"
		self.vibration_status = "on"
		self.sound_status = "on"
		self.delay = -5
		self.default_settings = "t"
	
class User:
	def __init__(self):
		self.username = ""
		self.password = ""
		self.email = ""
		self.G_key = ""
		self.settings = Settings()
		self.subjects = []
		self.prof = ""
		self.temp_subj =[]
		
class PolitoRequest:
	def __init__(self, materia, alfabetica, docente, codice):
		self.subject = materia
		self.alphabetic = alfabetica
		self.prof = docente
		self.code = codice
		self.uploaded = False
		
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
    textformatted.split('*')
    
    if len(textformatted) == 5:
    	result = PolitoCalendar(textformatted[0],textformatted[1],textformatted[2],textformatted[3])
    elif len(textformatted) == 4:
		result = PolitoCalendar(textformatted[0],"",textformatted[1],textformatted[2])
	return result


#HTML PAGES RENDERING

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
	if 'user' in session:
		return redirect ( url_for('default_user')+"?page=first")
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
	if session['user'] != 'ghost':
		return redirect(url_for('default_user'))
		
	session['user']='ghost'
	
	return render_template('registration.html', error=request.args.get('error'),
												mail=request.args.get('mail'),
												psw=request.args.get('psw'),
												usrname=request.args.get('usrname'))

@app.route('/architecture')
def architecture():
	return render_template('architecture.html')
	
@app.route('/user', methods=['POST', 'GET'])
def default_user():
	global All_user
	if 'user' in session:
		return render_template('default_user.html', delay=All_user[session['user']].settings.delay, 
													system=All_user[session['user']].settings.system_status,
													vibration=All_user[session['user']].settings.vibration_status, 
													sound=All_user[session['user']].settings.sound_status,
													default=All_user[session['user']].settings.default_settings,
													user_key=All_user[session['user']].G_key,
													prof=All_user[session['user']].prof,
													page=request.args.get('page'),
													select=request.args.get('select'),
													All_user=All_user)
		
	else:
		return redirect(url_for('login'))
	
  

#OPERATIVE URLS

@app.route('/newuser', methods=['POST', 'GET'])		#CREATION OF A NEW USER
def newuser():
	global All_user
	flag_ghost=False								#flag_ghost VARIABLE IS NEEDED TO CHECK IF THE USER IS ALREADY LOGGED
	temp=User()										#LOGGED-IN (IN THIS CASE HE MUST LOGOUT) OR NOT

	if session['user'] == 'ghost':
		flag_ghost=True
		
	else: 
		return redirect(url_for('login'))
	
	email=request.form.get('email')							#COLLECTING DATA FROM FORM IN REGISTRATION PAGE
	email_rep=request.form.get('email_rep')
	password=request.form.get('password')
	password_rep=request.form.get('password_rep')
	username=request.form.get('username')
	
	error=False
	mail=""
	psw=""
	usrname=""
	
	if (email == "" or email_rep == "" or email != email_rep) and flag_ghost == True:					#THE FOLLOWING 4 IF CONDION CHECK IF 
																										#THE FORM IS FILLED IN THE RIGHT WAY 
		error = True
		mail='mail=f'
	
	if (password == "" or password_rep == "" or password != password_rep) and flag_ghost == True:
		error = True
		psw='psw=f'
	
	if (username == "") and flag_ghost == True:
		error = True
		usrname='usrname=f'
	
	if error == True and flag_ghost == True:
		return redirect(url_for('registration')+"?error=t&"+mail+"&"+psw+"&"+usrname)
	
	
	temp.username=username				
	temp.password=password
	temp.email=email
	
	if username in All_user:										#IF THE USER ALREADY EXISTS THE NEW ONE IS ALERTED
		return redirect(url_for('login')+"?valid=extUsr")
	
	else:
		if 'credentials' not in session:												#CHECK FOR THE USER AUTHORIZATION
			return redirect(url_for('oauth2callback'))									#IF NOT PRESENT USER IS REDIRECTED 
																						#TO GOOGLE PAGE ASKING FOR PERMISSION	
		credentials = client.OAuth2Credentials.from_json(session['credentials'])
		
		if credentials.access_token_expired:
			return redirect(url_for('oauth2callback'))
			
		else:
			http_auth = credentials.authorize(httplib2.Http())
			service = discovery.build('calendar', 'v3', http_auth)
			
		calendar = {'summary': 'neverLate','timeZone': 'Europe/Rome'}					#NEVERLATE CALENDAR CREATION AND STORAGE 
																						#OF CALENDAR KEY
		created_calendar = service.calendars().insert(body=calendar).execute()
		
		temp.G_key=created_calendar['id']
			
		All_user[username]=temp
		session['user']=username
		
		return redirect(url_for('login'))
		
@app.route('/oauth2callback')		#GOOGLE CALENDAR PAGE ASKING FOR USER AUTHORIZATION, STANDARD FUNCTION
def oauth2callback():
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
           	return redirect(url_for('index'))

@app.route('/loggining', methods=['POST', 'GET'])	#CREATION A SESSION FROM AN EXISTING USER
def loggining():
	global All_user
	username=request.form.get('username')
	password=request.form.get('password')
	
	if username in All_user:											#CHECK FOR AN EXISTING USER AND
		check=All_user[username]										#EVENTUALLY IF USER'S PASSWORD IS CORRECT		
		if check.password == password:
			session['user']=username
			return redirect( url_for('default_user')+"?page=first")		
		else:
			return redirect(url_for('login')+"?valid=PswF")
	else:
		if username == "":
			return redirect(url_for('login')+"?valid=NoUsr")
			
		else:
			return redirect(url_for('login')+"?valid=UsrF")
			
@app.route('/G_key_mod', methods=['POST', 'GET'])	#GOOGLE CALENDAR KEY MODIFICATION
def Gkeymod():
	key=request.form.get('G_key')
	
	All_user[session['user']].G_key=key
	
	return redirect(url_for('default_user')+"?page=first")
	
@app.route('/settings_definition', methods=['POST', 'GET']) #PERSONAL SETTINGS CUSTOMIZATION
def settings_def():
	if 'user' in session:
		temp=All_user[session['user']]					#LOCAL COPY OF USER IN SESSION
													
		system=request.form.get('system')				#STORAGE OF NEW SETTINGS STATUS
		vibration=request.form.get('vibration')
		sound=request.form.get('sound')
		delay=request.form.get('delay')
		
		temp.settings.system_status=system				#NEW SETTINGS STORAGE AT METHOD LEVEL
		temp.settings.vibration_status=vibration
		temp.settings.sound_status=sound
		temp.settings.delay=delay
		temp.settings.default_settings="f"
		
		All_user[session['user']]=temp					#NEW SETTINGS STORAGE AT DATABASE LEVEL
		
		return redirect( url_for('default_user')+"?page=settings")
	
@app.route('/calendar_step1', methods=['POST', 'GET'])		#NEW SUBJECT SEARCH
def cal_step1():
	global urlAPIpolito
	
	All_user[session['user']].prof=""					#THIS VARIABLE IS USED AS A KEY SEARCHING NEW SUBJECTS
	All_user[session['user']].temp_subj=[]				#THIS VARIABLE IN USER OBJECT IS NEEDED TO SHOW A DIFFERENT SUBJECT LIST FOR EACH DIFFERENT USER
	All_user[session['user']].prof=request.form.get('newprof')
	
	if All_user[session['user']].prof == "":
		All_user[session['user']].temp_subj=[]
		return redirect(url_for('default_user')+"?page=calendar")
	
	APIrequest = requests.post(urlAPIpolito, json= { 'txt': All_user[session['user']].prof })		#COMUNICATION WITH POLITO API
	
	received=APIrequest.json()
	
	APIrequest.close()
	
	temp=[]						
	
	if received['d']:						#CONDITION CHECKING ELEMENTS ON RESPONSE LIST															
		for element in received['d']:
			temp_obj=PolitoRequest(element['materia'], element['alfabetica'], element['docente'], element['chiave'])	#IMPORTING RESPONSE ELEMENTS
			temp.append(temp_obj)	   			#LOCAL STORAGE OF RESPONSE ELEMENTS		
		
	#********************************
	
	if temp:						#CHECK OF LOCAL DATA (IF PRESENT OR NOT)
		for subject in temp:
			flag=True
			for personal_subj in All_user[session['user']].subjects and flag:			#ONLY THE SUBJECTS NOT IN THE USER'S PERSONAL DATA ARE STORED TEMPORARLY 
				if subject.code == personal_subj.code:									#IN THE DATABASE
					flag = False
			if flag:
				All_user[session['user']].temp_subj.append(subject.page_string())
			
		if not All_user[session['user']].temp_subj:
			return redirect(url_for('default_user')+"?page=calendar&select=empty")
		
		else:
			return redirect(url_for('default_user')+"?page=calendar")
			
	else:
		return redirect(url_for('default_user')+"?page=calendar&select=empty")

@app.route('/calendar_step2', methods=['POST', 'GET'])		#NEW SUBJECT ADDITION
def cal_step2():
	temp=request.form.get('subjects')		
	
	exit = True
	
	if subject:
		for subject in All_user[session['user']].temp_subj:
			if subject.page_string() == temp and exit:					#IF THERE IS A MATCH BETWEEN THE SELECTED ITEM AND ANY ELEMENT IN THE TEMPORARLY SUBJECT LIST  
				All_user[session['user']].subjects.append(subject)		#STORED IN DATABASE, THE SUBJECT IS ADDED IN THE USER'S OFFICIAL SUBJECT LIST
				exit = False
	
	for subject in All_user[session['user']].subjects:														#SYNCRONIZATION WITH GOOGLE CALENDAR IS CHECKED FOR 
		if subject.uploaded == False:																		#EACH ELEMENT OF THE USER'S OFFICIAL SUBJECT LIST
			scheduleParameters = { 'listachiavimaterie': subject.code, 'datarif': str(date.today())}
   		 	APIrequest = requests.post(urlScheduleTime, json=scheduleParameters)
    		schedule = APIrequest.json()
    		APIrequest.close()
    		
    		OneWeekSpan= timedelta(7,0,0)+DateFormat(schedule['d'][0]['start'])
    		
    		if schedule['d']:
    			for item in schedule['d']:
    				if DateFormat(item['start']) < OneWeekSpan:
    					event=PolitoCalendar()
    					
    					event=format_schedule(item['text'])
    					
    					event.start=item['start']
    					event.end=item['end']
    					
    					G_cal_request= {"end":{ "dateTime": event.end,"timeZone":"Europe/Rome"},
    									"start":{"dateTime": event.start,"timeZone":"Europe/Rome"},
    									"recurrence":["RRULE:FREQ=WEEKLY;UNTIL=20150631T170000Z"],
                    					"summary": event.subject+' '+event.professor,
                    					"description": event.comment,
                    					"location": event.classroom,
                    					"colorId":"3"}
                    
                    	try:				
                    		created_event=service.events().insert(calendarId=calendarid, body=event).execute()
                    		subject.uploaded=True
            
            else:
            	pass
			
	All_user[session['user']].temp_subj=[]
	All_user[session['user']].prof=""
	return redirect(url_for('default_user')+"?page=calendar")
		
@app.route('/logout')						#LOGOUT FUNCTION
def logout():
	del session['user']
	return redirect(url_for('index'))



#MAIN

if __name__ == '__main__':
	user=User()
	user.username='Riccardo'
	user.password='Gavoi91'
	All_user[user.username]=user
	app.run(debug=True, host='0.0.0.0')
	pass
