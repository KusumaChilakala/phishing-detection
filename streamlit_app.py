import streamlit as st
import pickle
import re

# Load model
model = pickle.load(open("model.pkl", "rb"))

st.set_page_config(page_title="Phishing Detection", layout="centered")

st.title("🔐 Phishing URL Detection System")
st.write("Enter a URL to check whether it is **Phishing** or **Legitimate**")

# Input URL
url = st.text_input("Enter URL")

def extract_features(url):
    return [
        len(url),
        url.count('.'),
        url.count('-'),
        url.count('@'),
        url.count('?'),
        url.count('%'),
        url.count('='),
        url.count('http'),
        url.count('https'),
        1 if re.search(r'\d', url) else 0
    ]

# Predict button
if st.button("Check URL"):
    if url == "":
        st.warning("Please enter a URL")
    else:
        features = extract_features(url)
        prediction = model.predict([features])

        if prediction[0] == 1:
            st.error("⚠️ Phishing Website Detected")
        else:
            st.success("✅ Legitimate Website")
