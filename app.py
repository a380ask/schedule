from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo


app = Flask(__name__)
app.url_map.strict_slashes = False
app.debug = True
app.secret_key = "jai"

try:
    username = "schedule"
    password = "kbqpaghOoNzHWQhO"
    dbname = "schedule"
    app.config[
        "MONGO_URI"] = "mongodb://schedule:kbqpaghOoNzHWQhO@cluster0-shard-00-00-n27aa.mongodb.net:27017," \
                       "cluster0-shard-00-01-n27aa.mongodb.net:27017," \
                       "cluster0-shard-00-02-n27aa.mongodb.net:27017/schedule?ssl=true&replicaSet=Cluster0-shard-0" \
                       "&authSource=admin&retryWrites=true&w=majority"
    mongo = PyMongo(app)
    print("connected!")
except:
    print("Cannot connect")

@app.route("/")
def index():
    return "Scheduling assistant"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        email_db = mongo.db.user.find({})
        for u in email_db:
            if str(email) == str(u["email"]) and str(password) == str(u["password"]):
                session['username'] = email
                user = mongo.db.user.find({})
                for id in user:
                    if str(email) == str(id["email"]):
                        return redirect(url_for('schedule', id=id["_id"]))
        else:
            print("Unsuccess")
            return render_template('login.html', message="Invalid login credentials")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = str(request.form.get('name'))
        email = request.form.get('email')
        print(f"email: {email}")
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        email_db = mongo.db.user.find({})
        for user in email_db:
            if email == user["email"]:
                message = "Email exists. Please login."
                print(message)
                return redirect(url_for('register'))
            elif password != confirm:
                message = "Passwords do not match. Please check."
                print(message)
                return redirect(url_for('register'))
            else:
                mongo.db.user.insert_one({"name": name, "email": email, "password": password})
                session['username'] = email
                id_db = mongo.db.user.find({})
                for id in id_db:
                    print(id["_id"])
                    return redirect(url_for('schedule', id=id["_id"]))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/schedule/<id>", methods=["GET", "POST"])
def schedule(id):
    if request.method == 'GET':
        user = mongo.db.user.find({})
        id = str(id)
        for i in user:
            i_id = str(i["_id"])
            if id == i_id:
                email = i["email"]
                name = i["name"]
                id = i["_id"]
                return render_template('schedule.html', email=email, name=name, id=id)
            else:
                pass
    else:
        title = request.form.get('title')
        date = request.form.get('date')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        user_id = id
        desc = request.form.get('desc')
        mongo.db.schedule_table.insert_one({"user_id":user_id, "title":title, "date":date, "time_start":time_start, "time_end":time_end, "desc":desc})
        return redirect(url_for('viewSchedule', id=user_id))

@app.route("/viewSchedule/<id>", methods=['GET'])
def viewSchedule(id):
    schedule = mongo.db.schedule_table.find({'user_id':id})
    user = mongo.db.user.find({})
    for a in user:
        if str(a['_id']) == str(id):
            name = a['name']
            email = a['email']
    return render_template('viewSchedule.html', schedule=schedule, id=id, name=name, email=email)

@app.route("/enterHours/<id>", methods=['GET', 'POST'])
def enterHours(id):
    if request.method == 'GET':
        user = mongo.db.user.find({})
        id_i = str(id)
        time = mongo.db.time.find({'user_id':id})
        for i in user:
            if str(i['_id']) == id_i:
                email = i["email"]
                name = i["name"]
                id = i["_id"]
                return render_template('hours.html', email=email, name=name, id=id, time=time)
    else:
        hours = request.form.get('hours')
        min = request.form.get('min')
        date = request.form.get('date')
        mongo.db.time.insert_one({"user_id":id, "hours":hours, "min":min, "date":date})
        return redirect(url_for('enterHours', id=id))
# run
if __name__ == "__main__":
    app.run()