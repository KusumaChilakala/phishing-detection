import numpy as np
from flask import Flask, request, jsonify, render_template
import joblib
import sqlite3
import pandas as pd
from sklearn import metrics
import warnings
import pickle
warnings.filterwarnings('ignore')
from feature import FeatureExtraction
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import os   # <-- added

app = Flask(__name__)

# ---------- MODEL LOAD + PATCH ----------
with open("model.pkl", "rb") as file:
    gbc = pickle.load(file)

if not hasattr(gbc, "_label_encoder"):
    gbc._label_encoder = LabelEncoder()
    gbc._label_encoder.classes_ = np.array([0, 1])
# ---------------------------------------

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/url", methods=["GET", "POST"])
def url():
    if request.method == "POST":
        url = request.form["url"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1, 30)
        y_pred = gbc.predict(x)[0]
        y_pro_phishing = gbc.predict_proba(x)[0, 0]
        y_pro_non_phishing = gbc.predict_proba(x)[0, 1]
        return render_template('result.html', xx=round(y_pro_non_phishing, 2), url=url)
    return render_template("index.html", xx=-1)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/logon')
def logon():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('signin.html')

# ---------------- FIXED SIGNUP ----------------
@app.route("/signup", methods=["POST"])   # <-- FIX: POST instead of GET
def signup():
    global otp, username, name, email, number, password

    # ❌ OLD (INSECURE)
    # username = request.args.get('user', '')
    # name = request.args.get('name', '')
    # email = request.args.get('email', '')
    # number = request.args.get('mobile', '')
    # password = request.args.get('password', '')

    # ✅ NEW (SECURE)
    username = request.form.get('user')
    name = request.form.get('name')
    email = request.form.get('email')
    number = request.form.get('mobile')
    password = request.form.get('password')

    otp = random.randint(1000, 5000)
    print("Generated OTP:", otp)

    try:
        msg = EmailMessage()
        msg.set_content("Your OTP is : " + str(otp))
        msg['Subject'] = 'OTP Verification'
        msg['From'] = "myprojectstp@gmail.com"
        msg['To'] = email

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()

        # ❌ OLD (BLOCKED BY GOOGLE)
        # s.login("myprojectstp@gmail.com", "paxgxdrhifmqcrzn")

        # ✅ NEW (USE APP PASSWORD)
        EMAIL_USER = "myprojectstp@gmail.com"
        EMAIL_PASS = "zlatqeslucvneorp"  # <-- replace this

        # ✅ OPTIONAL (BEST PRACTICE)
        # EMAIL_USER = os.getenv("EMAIL_USER")
        # EMAIL_PASS = os.getenv("EMAIL_PASS")

        s.login(EMAIL_USER, EMAIL_PASS)
        s.send_message(msg)
        s.quit()

        return render_template("val.html")

    except Exception as e:
        print("Email Error:", e)
        return "Error sending OTP. Check email configuration."

# ---------------- OTP VERIFY ----------------
@app.route('/predict1', methods=['POST'])
def predict1():
    global otp, username, name, email, number, password

    message = request.form['message']
    if int(message) == otp:
        con = sqlite3.connect('signup.db')
        cur = con.cursor()
        cur.execute(
            "INSERT INTO info (user, email, password, mobile, name) VALUES (?, ?, ?, ?, ?)",
            (username, email, password, number, name)
        )
        con.commit()
        con.close()
        return render_template("signin.html")

    return render_template("signup.html")

# ---------------- SIGNIN ----------------
@app.route("/signin")
def signin():
    mail1 = request.args.get('user', '')
    password1 = request.args.get('password', '')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("SELECT user, password FROM info WHERE user = ? AND password = ?", (mail1, password1))
    data = cur.fetchone()
    con.close()

    if data:
        return render_template("index.html")
    return render_template("signin.html")

@app.route("/notebook")
def notebook():
    return render_template("notebook.html")

if __name__ == "__main__":
    app.run(debug=True)
