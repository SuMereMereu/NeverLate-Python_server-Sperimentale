'''
Created on 04/mag/2015
@author: nicola, riccardo
'''
from flask import Flask , render_template, request, session, url_for, redirect

app = Flask(__name__)
app.secret_key='chiavesegreta'
All_user = {}
errorList = []
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
		self.G_key="0kobc6opfjckts9m15gs4p9adk%40group.calendar.google.com" #settare vuota e mettere form per inserire chiave
		self.settings=Settings()
		self.subjects=[]

#RENDERING PAGINE

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
	if 'user' in session:
		return redirect ( url_for('default_user'))

	return render_template('login.html', validation_login=request.args.get('valid'))
	
@app.route('/vision')
def vision():
    return render_template('vision.html')
    
@app.route('/requirements')
def requirements():
    return render_template('requirements.html')
    
@app.route('/registration', methods=['POST', 'GET'])
def registration():
	
	global errorList
	return render_template('registration.html', error=request.args.get('error'), errors=errorList)
	
@app.route('/architecture')
def architecture():
	return render_template('architecture.html')
	
@app.route('/user', methods=['POST', 'GET'])
def default_user():
	if 'user' in session:
		temp=All_user[session['user']]
		return render_template('default_user.html', delay=All_user[session['user']].settings.delay, 
													system=All_user[session['user']].settings.system_status,
													vibration=All_user[session['user']].settings.vibration_status, 
													sound=All_user[session['user']].settings.sound_status,
													default=All_user[session['user']].settings.default_settings,
													user_key=All_user[session['user']].G_key,
													page=request.args.get('page'))
		
	else:
		return redirect(url_for('login'))
	
  

#ROUTES OPERATIVE

@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
	global All_user
	global errorList
	
	temp=User()
	
	email=request.form.get('email')
	email_rep=request.form.get('email_rep')
	password=request.form.get('password')
	password_rep=request.form.get('password_rep')
	username=request.form.get('username')
	
	errorList=[]
	error=False
	
	if email == "" or email_rep == "" or email != email_rep:
		error = True
		errorList.append('Email field')
	
	if password == "" or password_rep == "" or password != password_rep:
		error = True
		errorList.append('Password field')
	
	if username == "":
		error = True
		errorList.append('Username field')
	
	if error == True:
		return redirect(url_for('registration')+"?error=t")
	
	temp.username=username
	temp.password=password
	temp.email=email
	
	if username in All_user:
		return redirect(url_for('login')+"?valid=extUsr")
	
	else:
		All_user[username]=temp
		session['user']=username
		
		return redirect(url_for('login'))

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
	temp_prof=request.form.get('newprof')
	print temp_prof
	return redirect(url_for('default_user')+"?page=calendar")

@app.route('/settings_definition', methods=['POST', 'GET']) #CANCELLARE LE PRINT
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
		
		print 'LOCAL'
		print 'system', system
		print 'vibration', vibration
		print 'sound', sound
		print 'delay', delay
		
		print 'ALL_USER'
		print All_user[session['user']].settings.system_status
		print All_user[session['user']].settings.vibration_status
		print All_user[session['user']].settings.sound_status
		print All_user[session['user']].settings.delay
		
		return redirect( url_for('default_user')+"?page=settings")
		
@app.route('/logout')
def logout():
	del session['user']
	return redirect(url_for('index'))

if __name__ == '__main__':
    user=User()
    user.username='admin'
    user.password='secretkey'
    All_user[user.username]=user
    app.run(debug=True)
    pass