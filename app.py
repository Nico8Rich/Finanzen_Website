from flask import Flask, render_template, url_for, request, redirect, flash, has_request_context
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()

class NewFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote = request.remote_addr
        else:
            record.url = None
            record.remote = None
        return super().format(record)


logFormatter = NewFormatter("%(asctime)s - %(url)s - %(remote)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

# add console handler to thw root logger
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

    
# add file handler to thw root logger
fileHandler = RotatingFileHandler("./logs/logs.log", backupCount=1, maxBytes=1000000000)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finanzen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mein schöner secret key'

db = SQLAlchemy(app)
app.app_context().push()

class Spenden(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unternehmen = db.Column(db.String(100), nullable=False)
    geld = db.Column( db.Float(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr(self):
        return '<Task %r' % self.id

class Ausgaben(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zweck = db.Column(db.String(200), nullable=False)
    geld = db.Column(db.Float(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr(self):
        return '<Task %r' % self.id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Integer, nullable=False)

    def __repr(self):
        return '<Task %r' % self.id



@app.route("/", methods=['POST', 'GET'])
def index():
    app.logger.info("Index start...")
    if request.method == 'POST':
        content_s = request.form.get('unternehmen')
        content_a = request.form.get('grund')
        geld_s = request.form.get('geld_s')
        geld_a = request.form.get('geld_a')

        if content_s and geld_s and content_a and geld_a:
            new_entry_spenden = Spenden(unternehmen=content_s, geld=geld_s)
            new_entry_ausgaben = Ausgaben(zweck=content_a, geld=geld_a)
            try:
                db.session.add(new_entry_spenden)
                db.session.commit()
                db.session.add(new_entry_ausgaben)
                db.session.commit()
                return redirect('/index.html')
            except:
                return 'There was an issue with the Entry entry'

        elif content_s and geld_s:
            new_entry_spenden = Spenden(unternehmen=content_s, geld=geld_s)
            try:
                db.session.add(new_entry_spenden)
                db.session.commit()
                return redirect('/index.html')
            except:
                return 'There was an issue with the Spenden entry'
        
        elif content_a and geld_a:
            new_entry_ausgaben = Ausgaben(zweck=content_a, geld=geld_a)
            try:
                db.session.add(new_entry_ausgaben)
                db.session.commit()
                return redirect('/index.html')
            except:
                return 'There was an issue with the Ausgaben entry'
        return render_template('index.html')
    else:
        return render_template('/index.html')



@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)            
            return redirect(url_for('secure'))
            
        else:
            return render_template('login.html')
        
    else:
        return render_template('login.html')

# Flask-Login initialisieren
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

@app.route('/secure.html', methods=['GET', 'POST'])
@login_required
def secure():
    if current_user.is_authenticated:
        app.logger.info("Secure start," +  current_user.username)
    else:
        app.logger.info("Secure start")
    if request.method == 'POST':
        content_s = request.form.get('unternehmen')
        content_a = request.form.get('grund')
        geld_s = request.form.get('geld_s')
        geld_a = request.form.get('geld_a')

        if content_s and geld_s and content_a and geld_a:
            new_entry_spenden = Spenden(unternehmen=content_s, geld=geld_s)
            new_entry_ausgaben = Ausgaben(zweck=content_a, geld=geld_a)
            try:
                db.session.add(new_entry_spenden)
                db.session.commit()
                db.session.add(new_entry_ausgaben)
                db.session.commit()
                return redirect('/secure.html')
            except:
                return 'There was an issue with the Entry entry'

        elif content_s and geld_s:
            new_entry_spenden = Spenden(unternehmen=content_s, geld=geld_s)
            try:
                db.session.add(new_entry_spenden)
                db.session.commit()
                return redirect('/secure.html')
            except:
                return 'There was an issue with the Spenden entry'
        
        elif content_a and geld_a:
            new_entry_ausgaben = Ausgaben(zweck=content_a, geld=geld_a)
            try:
                db.session.add(new_entry_ausgaben)
                db.session.commit()
                return redirect('/secure.html')
            except:
                return 'There was an issue with the Ausgaben entry'
        return render_template('secure.html')
    else:
        return render_template('secure.html')

@app.route('/spenden.html')
@login_required
def spenden():
    spenden = Spenden.query.order_by(Spenden.id).all()# Alle Spenden aus der Datenbank abrufen
    return render_template('spenden.html', spenden=spenden) 

@app.route('/ausgaben.html')
@login_required
def ausgaben():
    ausgaben = Ausgaben.query.order_by(Ausgaben.id).all()  # Alle Ausgaben aus der Datenbank abrufen
    return render_template('ausgaben.html', ausgaben=ausgaben)

@app.route('/bilanz.html')
@login_required
def bilanz():
    spenden = Spenden.query.order_by(Spenden.id).all()
    ausgaben = Ausgaben.query.order_by(Ausgaben.id).all()
    summe_spenden = 0
    summe_ausgaben = 0

    for spende in spenden:
        summe_spenden += spende.geld

    for ausgabe in ausgaben:
        summe_ausgaben += ausgabe.geld

    bilanz = summe_spenden - summe_ausgaben
    if bilanz >= 0:
        farbe = '#0ab40a'
    else:
        farbe = '#b4320a'
    return render_template('bilanz.html', bilanz=bilanz, farbe=farbe)

@app.route('/delete_spende/<int:id>')
def delete_spende(id):
    spende_to_delete = Spenden.query.get_or_404(id)
    need = Spenden.query.filter_by(id=id)
    try:
        app.logger.info("Delete a message by " + current_user.username + " Deleting Message: " + need)
        db.session.delete(spende_to_delete)
        db.session.commit()
        return redirect('/spenden.html')

    except:
        return 'There was a problem deleting that donation'

@app.route('/datenschutz')    
def datenschutz():
    return render_template('datenschutz.html')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               

@app.route('/delete_ausgabe/<int:id>')
def delete_ausgabe(id):
    ausgabe_to_delete = Ausgaben.query.get_or_404(id)

    try:
        app.logger.info("Delete a message by " + current_user.username + " Deleting Message: ")
        db.session.delete(ausgabe_to_delete)
        db.session.commit()
        return redirect('/ausgaben.html')

    except:
        return 'There was a problem deleting that Expense' 

# Spenden.query.order_by(id).all() listet alle werte auf

"""
# Überprüfen, ob der Benutzer bereits existiert
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Benutzername existiert bereits.', 'danger')
        else:

"""


if __name__ == '__main__':
    app.run(debug=True)