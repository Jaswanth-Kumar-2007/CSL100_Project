from flask import Flask,render_template,url_for,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    userid = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))

    def __init__(self,userid,password,name):
        self.userid=userid
        self.password=password
        self.name=name

    def check_password(self,password):
        if self.password == password:
            return True
        else:
            return False

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(200),nullable=False)
    progress= db.Column(db.Integer,default=0)
    topic = db.Column(db.String(100))
    assignon = db.Column(db.String(10))
    assigne = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    priority = db.Column(db.String(20),nullable=False)
    deadline = db.Column(db.String(10))
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #def __repr__(self):
        #return '<Task%r'%self.id

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_text = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@ app.route('/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        
        user = User.query.filter_by(userid=userid).first()

        if user and user.check_password(password):
            session['name'] = user.name
            session['userid'] = user.userid
            session['password'] = user.password
            return redirect('/dashboard')
        elif userid == "admin" and password == "admin@123":
            return redirect('/admin')
        else:
            return render_template('login.html',error='Invalid User')

    return render_template("login.html")

@ app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        userid = request.form['userid']
        password = request.form['password']

        existing_user = User.query.filter_by(userid=userid).first()
        if existing_user:
            return render_template('register.html', error='UserID already exists!')

        new_user = User(name=name,userid=userid,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template("register.html",error='Already Exists')

@app.route('/admin')
def admin():
    users = User.query
    return render_template('admin.html',users=users)

@app.route('/de/<int:id>')
def de(id):
    note_to_delete = User.query.get_or_404(id)
    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return redirect('/admin')
    except:
        return "There was an error"

@app.route('/dashboard')
def dashboard():
    if session['name']:
        user = User.query.filter_by(userid=session['userid']).first()
        return render_template('dashboard.html',user=user)
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('userid',None)
    return redirect('/')

@app.route('/todo',methods=['POST','GET'])
def index():
    if 'userid' not in session:
        return redirect('/')
    else:
        current_user = User.query.filter_by(userid=session['userid']).first()
        tasks = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.date_created)
        return render_template('Task.html',tasks=tasks)

@app.route('/addtask',methods=['POST','GET'])
def addtask():
    if 'userid' not in session:
        return redirect('/')

    current_user = User.query.filter_by(userid=session['userid']).first()
    if request.method == 'POST':
        task_content = request.form['todo']
        progress = request.form['progress']
        topic = request.form['topic']
        deadline = request.form['deadline']
        assigne = request.form['assigne']
        description = request.form['description']
        priority = request.form['priority']
        assignon = request.form['assignon']
        new_task = Todo(content=task_content,progress=progress,topic=topic,deadline=deadline,assigne=assigne,description=description,priority=priority,assignon=assignon,user_id=current_user.id)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('todo')
        except:
            return "There was an Issue"  
    else:
        return render_template('addtask.html')  

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/todo')
    except:
        return "There was a error"

@ app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.progress = request.form['progress']
        task.topic = request.form['topic']
        task.deadline = request.form['deadline']
        task.description = request.form['description']
        task.assignon = request.form['assignon']
        task.priority = request.form['priority']
        task.assigne = request.form['assigne']

        try:
            db.session.commit()
            return redirect('/todo')
        except:
            return 'There was an error'
    else:
        return render_template('updatetask.html',task=task)

@app.route('/personalnotes',methods=['POST','GET'])
def personalnotes():
    if 'userid' not in session:
        return redirect('/')

    current_user = User.query.filter_by(userid=session['userid']).first()
    if request.method == 'POST':
        personal_notes = request.form['notes']
        new_notes = Note(note_text=personal_notes,user_id=current_user.id)

        try:
            db.session.add(new_notes)
            db.session.commit()
            return redirect('/personalnotes')
        except:
            return "There was an Issue"  
    else:
        notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.date_created)
        return render_template('personalnotes.html',notes=notes)    

@app.route('/del/<int:id>')
def dele(id):
    note_to_delete = Note.query.get_or_404(id)
    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return redirect('/personalnotes')
    except:
        return "There was an error"

@app.route('/upd/<int:id>',methods=['POST','GET'])
def upda(id):
    note = Note.query.get_or_404(id)
    if request.method == 'POST':
        note.note_text = request.form['updanote']

        try:
            db.session.commit()
            return redirect('/personalnotes')
        except:
            return "There was an error"
    else:
        return render_template('updatenotes.html',note=note)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)