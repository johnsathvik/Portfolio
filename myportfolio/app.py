from flask import Flask, render_template, request
from firebase import firebase

app = Flask(__name__)
fb = firebase.FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/', None)

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

@app.route('/contact', methods=["POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        cli_email = request.form.get('email')
        sub = request.form.get('subject')
        message = request.form.get('message')
        print(f"Contact from {name} ({cli_email}) - {sub}: {message}")
        return "OK"

if __name__ == "__main__":
    app.run(port=5000)
