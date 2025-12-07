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
from sklearn.preprocessing import LabelEncoder  # <-- added import

app = Flask(__name__)

# ---------- MODEL LOAD + PATCH ----------
with open("model.pkl", "rb") as file:
    gbc = pickle.load(file)

# --- PATCH for old StackingClassifier missing _label_encoder ---
if not hasattr(gbc, "_label_encoder"):
    gbc._label_encoder = LabelEncoder()
    gbc._label_encoder.classes_ = np.array([0, 1])  # change if your labels differ
# ---------------------------------------------------------------

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
        # 1 is safe, -1 is unsafe
        y_pro_phishing = gbc.predict_proba(x)[0, 0]
        y_pro_non_phishing = gbc.predict_proba(x)[0, 1]

        pred = "It is {0:.2f}% safe to go ".format(y_pro_phishing * 100)
        return render_template('result.html', xx=round(y_pro_non_phishing, 2), url=url)
    return render_template("index.html", xx=-1)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/logon')
def logon():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('signin.html')

@app.route("/signup")
def signup():
    global otp, username, name, email, number, password
    username = request.args.get('user', '')
    name = request.args.get('name', '')
    email = request.args.get('email', '')
    number = request.args.get('mobile', '')
    password = request.args.get('password', '')
    otp = random.randint(1000, 5000)
    print(otp)

    msg = EmailMessage()
    msg.set_content("Your OTP is : " + str(otp))
    msg['Subject'] = 'OTP'
    msg['From'] = "myprojectstp@gmail.com"
    msg['To'] = email

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("myprojectstp@gmail.com", "paxgxdrhifmqcrzn")
    s.send_message(msg)
    s.quit()
    return render_template("val.html")

@app.route('/predict1', methods=['POST'])
def predict1():
    global otp, username, name, email, number, password
    if request.method == 'POST':
        message = request.form['message']
        print(message)
        if int(message) == otp:
            print("TRUE")
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

@app.route("/signin")
def signin():
    mail1 = request.args.get('user', '')
    password1 = request.args.get('password', '')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("SELECT user, password FROM info WHERE user = ? AND password = ?", (mail1, password1))
    data = cur.fetchone()

    if data is None:
        return render_template("signin.html")

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("index.html")
    else:
        return render_template("signin.html")

@app.route("/notebook")
def notebook():
    return render_template("notebook.html")

if __name__ == "__main__":
    app.run(debug=True)
