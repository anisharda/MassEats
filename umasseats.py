from flask import Flask, request, render_template, redirect, url_for, make_response
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:admin123@cluster0.key0u.mongodb.net/Connect?retryWrites=true&w=majority"
mongo = PyMongo(app)
sameTime = []


@app.route("/")
def welcome():
    return render_template('welcome.html')

# if __name__ == "main":
#     app.run()

@app.route('/register', methods=['GET', 'POST'])
def register():
    token = request.cookies.get('access_token')
    if token:
        return redirect(url_for('feed'))
    
    if request.method == "POST":
        _name = request.form.get('name')
        _email = request.form.get('email')
        _phone = request.form.get('phone')
        _username = request.form.get('username')
        _password = request.form.get('password').encode('utf-8')
        hashPassword = bcrypt.hashpw(_password, bcrypt.gensalt())
        
        
        #print(_name,_password)
        mongo.db.people.insert_one({'name': _name, 'email': _email, 'phone':_phone,'username':_username, 'password': hashPassword,})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    token = request.cookies.get('access_token')
    if token:
        return redirect(url_for('feed'))
    
    if request.method == "POST":
        _username = request.form.get('username')
        _password = request.form.get('password').encode('utf-8')
        
        #print(_name,_password)
        # mongo.db.people.find_one({'name': _name, 'email': _email, 'phone':_phone,'username':_username, 'password': _password,})
    
        usernameCheck = mongo.db.people.find_one({'username':_username})

        if usernameCheck == None:
            return "This username is not found. Re-enter username"
                         
        
        if bcrypt.checkpw(_password, usernameCheck['password']):
            response = make_response(redirect(url_for('feed')))
            response.set_cookie("access_token", _username)
            return response
        else:
            return "password is wrong"

        return f'Hello, {_username}'
    return render_template('logIn.html')

@app.route('/feed', methods=['GET', 'POST'])
def feed():
    token = request.cookies.get('access_token')
    if token:
        timeCheck = mongo.db.schedule.find_one({'username': token})
        if timeCheck == None:
            return render_template('feed.html', scenario = 'Time not submitted')
        else:
            global sameTime
            sameTime = []
            userpreferences =[]
            _username = request.cookies.get('access_token')
            _time = mongo.db.schedule.find_one({'username': _username})['time']        
            for i in mongo.db.schedule.find({'time': _time}):
                sameTime.append(mongo.db.people.find_one({'username': i['username']}, {'password': 0}))
                userpreferences.append(mongo.db.preferences.find_one({'username': i['username']}))
            return render_template('feed.html', scenario = 'Time is submitted', sameTime= sameTime, pref= userpreferences)

    else:
        return redirect(url_for('login'))

@app.route('/checkbox', methods = ['GET', 'POST'])
def checkbox():
    return render_template('checkbox.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie("access_token", "", max_age = 0)
    return response

@app.route('/submitTime', methods = ['POST']) 
def submitTime():
    # global sameTime
    # sameTime = []
    _username = request.cookies.get('access_token')
    _time = request.form.get('time')

         
    # for i in mongo.db.schedule.find({'time': _time}):
    #     sameTime.append(mongo.db.people.find_one({'username': i['username']}, {'password': 0}))
     
    mongo.db.schedule.insert_one({'username':_username, 'time':_time})
     

    return redirect(url_for('feed'))

@app.route('/changeTime')
def changeTime():
    token = request.cookies.get('access_token')
    if token:
        if mongo.db.schedule.find_one({'username': token}):
            mongo.db.schedule.delete_one({'username': token})
            return redirect(url_for('feed'))

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if request.method == "POST":
        token = request.cookies.get('access_token')
        _pronouns = request.form.get('pronouns')
        _year = request.form.get('year')
        _major = request.form.get('major')
        _dininghall = request.form.get('dininghall')
        
        
        
        #print(_name,_password)
        mongo.db.preferences.insert_one({'username': token, 'pronouns': _pronouns, 'year': _year, 'major': _major, 'dininghall': _dininghall})        
        return redirect(url_for('feed'))
    return render_template('profile.html')

    # _major = request.form.get('major')
    # _dininghall = request.form.get('dininghall')
    # _bio = request.form.get('bio')   
        
    # mongo.db.people.insert_one({'major': _major, 'dininghall': _dininghall, 'bio':_bio})
    # return render_template('preferences.html')


