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
	print 'a'
	if 'user' in session:
		return redirect ( url_for('default_user'))
    
	print 'b'
	
	print request.args.get('valid')
	validation_login=request.args.get('valid')
	print validation_login
	return render_template('login.html', validation_login=request.args.get('valid'))

@app.route('/loggining', methods=['POST', 'GET'])
def loggining():
	global All_user
	username=request.form['username']
	password=request.form['password']
	
	check=All_user[username]
	
	if username in All_user and check.password == password:
		print user.username
		print user.password
		session['user']=username
		return render_template('default_user.html')
	
	else:
		return redirect(url_for('login')+"?valid=False")
	
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
	validation_reg=True
	email=request.form['email']
	email_rep=request.form['email_rep']
	
	if (email != email_rep):
		validation_reg=False
		redirect ( url_for('registration'))
	
	password=request.form['password']
	password_rep=request.form['password_rep']
	
	if (password != password_rep):
		validation_reg=False
		redirect ( url_for('registration'))
		
	username=request.form['username']
	

	
	user.username=username
	user.password=password
	user.email=email
	
	All_user[username] = user
	session['user']=username
	
	return redirect(url_for('login'))
	
	
@app.route('/registration', methods=['POST', 'GET'])
def registration():
    return render_template('registration.html')
    
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