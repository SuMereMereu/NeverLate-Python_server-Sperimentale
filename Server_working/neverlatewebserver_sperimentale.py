'''
Created on 04/mag/2015

@author: nicola, riccardo
'''
from flask import Flask , render_template, request, session, url_for, redirect

app = Flask(__name__)
app.secret_key='chiavesegreta'
All_user ={}

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
    
@app.route('/default_user')
def default_user():
	return render_template('default_user.html')
	
@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
	global All_user
	
	email=request.form.get('email')
	email_rep=request.form.get('email_rep')
	
	if (email != email_rep):
		redirect ( url_for('registration')+"?valid=repMailF")
		
	
	password=request.form.get('password')
	password_rep=request.form.get('password_rep')
	
	if (password != password_rep):
		redirect ( url_for('registration')+"?valid=repPswF")
		
		
	username=request.form.get('username')
	
	
	user.username=username
	user.password=password
	user.email=email
	
	if username in All_user:
		if password == All_user[username].password:
			session['user']=username
			print All_user
			return redirect(url_for('login')+"valid=extUsr")
			
		else:
			return redirect(url_for('registration')+"?valid=exUsr")
	
	else:
		All_user[username] = user
		session['user']=username
		
		print All_user
		
		return redirect(url_for('login'))
	
	
@app.route('/registration', methods=['POST', 'GET'])
def registration():
    return render_template('registration.html', validation_login=request.args.get('valid'))
    
@app.route('/architecture')
def architecture():
	return render_template('architecture.html')



#@app.route('/api/data',methods=['GET'])
 #def index():
 #   data=jsonifymysql
 #   return data


if __name__ == '__main__':
    user=utente()
    user.username='admin'
    user.password='secretkey'
    All_user = { user.username : user }
    app.run(debug=True)
    pass