'''
Created on 04/mag/2015
@author: nicola, riccardo
'''
from flask import Flask , render_template, request, session, url_for, redirect
from datetime import datetime, date, timedelta
from apiclient import discovery
from oauth2client import client
import json
import httplib2

app = Flask(__name__)
app.secret_key='chiavesegreta'
All_user = {}
Profs = {}

class Settings:
	def __init__(self):
		self.system_status="on"
		self.vibration_status="on"
		self.sound_status="on"
		self.delay=-5
		self.default_settings="t"
	
class User:
	def __init__(self):
		self.username=""
		self.password=""
		self.email=""
		self.G_key=""
		self.settings=Settings()
		self.subjects=[]
		self.prof=""
		self.temp_subj=[]

#RENDERING PAGINE

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
	if 'user' in session:
		return redirect ( url_for('default_user'))
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
	
  

#ROUTES OPERATIVE

@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
	global All_user
	flag_ghost=False
	temp=User()

	if session['user'] == 'ghost':
		flag_ghost=True
	
	email=request.form.get('email')
	email_rep=request.form.get('email_rep')
	password=request.form.get('password')
	password_rep=request.form.get('password_rep')
	username=request.form.get('username')
	
	error=False
	mail=""
	psw=""
	usrname=""
	
	if (email == "" or email_rep == "" or email != email_rep) and flag_ghost == True:
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
	
	if username in All_user:
		return redirect(url_for('login')+"?valid=extUsr")
	
	else:
		if 'credentials' not in session:
			return redirect(url_for('oauth2callback'))
		
		credentials = client.OAuth2Credentials.from_json(session['credentials'])
		
		if credentials.access_token_expired:
			return redirect(url_for('oauth2callback'))
			
		else:
			http_auth = credentials.authorize(httplib2.Http())
			service = discovery.build('calendar', 'v3', http_auth)
			
		calendar = {'summary': 'neverLate','timeZone': 'Europe/Rome'}
		
		created_calendar = service.calendars().insert(body=calendar).execute()
		
		temp.G_key=created_calendar['id']
			
		All_user[username]=temp
		session['user']=username
		
		return redirect(url_for('login'))
		
	
@app.route('/oauth2callback')
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

@app.route('/loggining', methods=['POST', 'GET'])
def loggining():
	global All_user
	username=request.form.get('username')
	password=request.form.get('password')
	
	if username in All_user:
		check=All_user[username]
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
	
@app.route('/calendar_step1', methods=['POST', 'GET'])
def cal_step1():
	if All_user[session['user']].prof == "":
		All_user[session['user']].prof=request.form.get('newprof')
	
	if All_user[session['user']].prof in Profs:
		All_user[session['user']].temp_subj=Profs[All_user[session['user']].prof]
		for subject in All_user[session['user']].subjects:
			if subject in All_user[session['user']].temp_subj:
				All_user[session['user']].temp_subj.remove(subject)
				
		if not All_user[session['user']].temp_subj:
			All_user[session['user']].prof=""
			return redirect(url_for('default_user')+"?page=calendar&select=empty")
		
		else:
			return redirect(url_for('default_user')+"?page=calendar")
			
	else:
		All_user[session['user']].prof=""
		return redirect(url_for('default_user')+"?page=calendar")

@app.route('/calendar_step2', methods=['POST', 'GET'])
def cal_step2():
	temp=request.form.get('subjects')
	All_user[session['user']].subjects.append(temp)
	All_user[session['user']].temp_subj=[]
	All_user[session['user']].prof=""
	return redirect(url_for('default_user')+"?page=calendar")

@app.route('/settings_definition', methods=['POST', 'GET'])
def settings_def():
	if 'user' in session:
		temp=All_user[session['user']]
		
		system=request.form.get('system')
		vibration=request.form.get('vibration')
		sound=request.form.get('sound')
		delay=request.form.get('delay')
		
		temp.settings.system_status=system
		temp.settings.vibration_status=vibration
		temp.settings.sound_status=sound
		temp.settings.delay=delay
		temp.settings.default_settings="f"
		
		All_user[session['user']]=temp
		
		return redirect( url_for('default_user')+"?page=settings")
		
@app.route('/logout')
def logout():
	del session['user']
	return redirect(url_for('index'))

if __name__ == '__main__':
	user=User()
	user.username='Riccardo'
	user.password='Gavoi91'
	user.subjects=['inf', 'analisi3', 'chimica', 'gianni']
	materie=['Ami', 'inf', 'gianni', 'analisi2']
	Profs['corno']=materie
	All_user[user.username]=user
	app.run(debug=True, host='0.0.0.0')
	pass
