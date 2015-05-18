'''
Created on 04/mag/2015

@author: nicola, riccardo
'''
from flask import Flask , render_template, request, session, url_for, redirect

app = Flask(__name__)
app.secret_key='chiavesegreta'
All_user = {}
errorList = []

class utente:
	def __init__(self):
		self.username=""
		self.password=""
		self.email=""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
	if 'user' in session:
		return redirect ( url_for('default_user'))

	return render_template('login.html', validation_login=request.args.get('valid'))

@app.route('/loggining', methods=['POST', 'GET'])
def loggining():
	global All_user
	print All_user
	username=request.form.get('username')
	password=request.form.get('password')
	
	print username
	
	if username in All_user:
		check=All_user[username]
		if check.password == password:
			session['user']=username
			return render_template('default_user.html')
		else:
			return redirect(url_for('login')+"?valid=PswF")
	else:
		if username == "":
			return redirect(url_for('login')+"?valid=NoUsr")
			
		else:
			return redirect(url_for('login')+"?valid=UsrF")
	
@app.route('/logout')
def logout():
	del session['user']
	return redirect(url_for('index'))
	
@app.route('/vision')
def vision():
    return render_template('vision.html')

@app.route('/requirements')
def requirements():
    return render_template('requirements.html')
    
@app.route('/user')
def default_user():
	if 'user' in session:
		return render_template('default_user.html')
		
	else:
		return redirect(url_for('login'))
	
@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
	global All_user
	global errorList
	
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
	
	user.username=username
	user.password=password
	user.email=email
	
	if username in All_user:
		return redirect(url_for('login')+"?valid=extUsr")
	
	else:
		All_user[username] = user
		session['user']=username
		
		return redirect(url_for('login'))
	
	
@app.route('/registration', methods=['POST', 'GET'])
def registration():
	
	global errorList
	return render_template('registration.html', error=request.args.get('error'), errors=errorList)
    
@app.route('/architecture')
def architecture():
	return render_template('architecture.html')

if __name__ == '__main__':
    user=utente()
    user.username='admin'
    user.password='secretkey'
    All_user = { user.username : user }
    app.run(debug=True)
    pass