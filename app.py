# app.py
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Watchlist
from forms import LoginForm, RegistrationForm
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = ''  # Cambia con una chiave segreta sicura



database_path = os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotte dell'applicazione
@app.route('/')
def index():
    response = requests.get('https://api.coingecko.com/api/v3/coins/markets', params={
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1
    })
    coins = response.json()
    return render_template('index.html', coins=coins)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registrazione completata. Ora puoi effettuare il login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Nome utente o password non corretti.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_to_watchlist/<coin_id>')
@login_required
def add_to_watchlist(coin_id):
    if not Watchlist.query.filter_by(user_id=current_user.id, coin_id=coin_id).first():
        watch_item = Watchlist(user_id=current_user.id, coin_id=coin_id)
        db.session.add(watch_item)
        db.session.commit()
        flash('Criptovaluta aggiunta alla tua watchlist.')
    else:
        flash('La criptovaluta è già nella tua watchlist.')
    return redirect(url_for('index'))

@app.route('/watchlist')
@login_required
def watchlist():
    watch_items = Watchlist.query.filter_by(user_id=current_user.id).all()
    coin_ids = [item.coin_id for item in watch_items]
    if coin_ids:
        response = requests.get('https://api.coingecko.com/api/v3/coins/markets', params={
            'vs_currency': 'usd',
            'ids': ','.join(coin_ids)
        })
        coins = response.json()
    else:
        coins = []
    return render_template('watchlist.html', coins=coins)

if __name__ == '__main__':
    app.run(debug=True)
