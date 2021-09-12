from flask import Flask, json, render_template, request, redirect, url_for, session
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
from flask.helpers import flash
from functools import wraps
import requests
from requests.structures import CaseInsensitiveDict

cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
app.secret_key = 'qwerty'

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash('anda harus login', 'danger')
            return redirect(url_for("login"))
    return wrapper

def send_wa(m, p):
    api = "ce3faa5dfaf8a23821bb44cd95108adef5a5ea8f"
    url = "https://starsender.online/api/sendFiles "

    data = {
        "tujuan": p,
        "message": m,
        "file": "https://timlo.net/wp-content/uploads/2020/10/The-Conjuring-2-Scrapped-Animatronic-Demon.jpg",
    }
    headers =  CaseInsensitiveDict
    headers['apikey'] = api

    res = requests.post(url, json=data, headers=headers)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        data ={
            'email': request.form['email'],
            'password': request.form['password']
        }

        users = db.collection("users").where('email','==', data['email']).stream()
        user = {}

        for us in users:
            user = us.to_dict()
        if user:
            if check_password_hash(user['password'], data['password']):
                session['user'] = user
                flash('selamat anda berhasil Log in', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('maaf password anda salah', 'danger')
                return redirect(url_for('login'))
        else:
            flash('email anda belum terdaftar', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('anda belum login', 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/mahasiswa')
@login_required
def mahasiswa():
    maba = db.collection("mahasiswa").stream()
    mb = []
    for mhs in maba:
        m = mhs.to_dict()
        m["id"] = mhs.id
        mb.append(m)
    return render_template('mahasiswa.html', data=mb)

@app.route('/mahasiswa/tambah', methods = ['GET', 'POST'])
def tambah_mhs():
    if request.method == 'POST':
        data = {
            "nama": request.form["nama"],
            "jurusan": request.form["jurusan"],
            "tanggal_lahir": request.form["tanggal_lahir"],
        }
        # ini fungsi untuk menambahkan data ke firebase
        db.collection("mahasiswa").document().set(data)
        flash('berhasil menambahkan data', 'success')
        return redirect(url_for('mahasiswa'))
    return render_template('add_mhs.html')

@app.route("/mahasiswa/hapus/<uid>")
def hapus_mhs(uid):
    db.collection('mahasiswa').document(uid).delete()
    flash('berhasil menghapus data', 'danger')
    return redirect(url_for("mahasiswa"))

@app.route("/mahasiswa/lihat/<uid>")
def lihat_mhs(uid):
    user = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template("lihat_mhs.html", user=user)

@app.route('/mahasiswa/ubah/<uid>', methods = ["GET", "POST"])
def ubah_mhs(uid):
    # menentukan method
    if request.method == 'POST':
        data = {
            "nama": request.form["nama"],
            "jurusan": request.form["jurusan"],
            "tanggal_lahir": request.form["tanggal_lahir"],
        }
        db.collection("mahasiswa").document(uid).set(data, merge = True)
        flash('berhasil mengubah data', 'primary')
        return redirect(url_for("mahasiswa"))
        # menerima data lama
        # set di database

        # mengambil data
    user = db.collection("mahasiswa").document(uid).get().to_dict()
    user['id'] = uid
    # render template
    return render_template('ubah_mhs.html', user=user)

@app.route('/register', methods = ["GET","POST"])
def register():
    if request.method == 'POST':
        data = {
            "username": request.form["username"],
            "email": request.form["email"],
            "nomor": request.form["nomor"],
        }
        users=db.collection('users').where('email','==', data['email']).stream()
        user = {}
        for us in users:
            user = us.to_dict()
        if user:
            flash('email sudah terdaftar','danger')
            return redirect(url_for('register'))

        data['password'] = generate_password_hash(request.form['password'], 'sha256')
        db.collection('users').document().set(data)
        # send_wa(f"halo  *{data['username']}*  saya valak", data)
        flash('Selamat, anda berhasil register','success')
        return redirect(url_for('login'))
    return render_template('register.html')

# stream : menampilkan semua data, get : menampilkan 1 data, to_dict : untuk menyajikan dalam bentuk dictionary

if __name__ == "__main__":
    app.run(debug=True)