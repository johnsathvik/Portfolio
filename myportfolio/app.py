from flask import Flask, render_template, request
from firebase import firebase
import smtplib
from email.mime.text import MIMEText
import requests

app = Flask(__name__)
fb = firebase.FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/', None)

def send_telegram_message(name, email, subject, message):
    #  bot token
    bot_token = '7634605210:AAGV3zH26-TjdCx25AjrLO8SG9EuRhJZRPs'
    chat_id = 914342868  # Target user's Telegram ID

    # Compose one-line message
    full_message = f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}"

    # Telegram API URL
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Payload for POST request
    payload = {
        'chat_id': chat_id,
        'text': full_message
    }

    # Send the message
    response = requests.post(url, data=payload)

    # Handle response
    if response.status_code == 200:
        print("Message sent successfully.")
        return True
    else:
        print(f"Failed to send message: {response.text}")
        return False

send_telegram_message(
    name="name",
    email="email",
    subject="subject",
    message="message"
)

@app.route('/')
def home():
    landing_data = fb.get('/landing', None) or {}
    about_data = fb.get('/about', None) or {}
    experience_data = fb.get('/experience', None) or {}
    education_data = fb.get('/resume/education', None) or {}
    links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None) or {}

    # Extract fields
    email = links.get('email', '')
    phone = links.get('phone', '')
    linkedin = links.get('linkedin', '')
    telegram = links.get('telegram', '')
    whatsapp = links.get('whatsapp', '')

    raw_skills = landing_data.get('skills-list', {})
    skills = []
    for block in raw_skills.values():
        skills.extend(block.get('skills', []))

    raw_bio = landing_data.get('bio', {})
    bio = next(iter(raw_bio.values())).get('bio', '') if raw_bio else ''

    about_skills = []
    for block in about_data.get('skills', {}).values():
        about_skills.extend(block.get('skills', []))

    return render_template(
        'index.html',
        skills=skills,
        bio=bio,
        about_skills=about_skills,
        experiences=experience_data,
        education=education_data,
        email=email,
        phone=phone,
        linkedin=linkedin,
        telegram=telegram,
        whatsapp=whatsapp
    )

@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        cli_email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        resp = send_telegram_message(name, cli_email, subject, message)
        return "OK"

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(port=5000)
