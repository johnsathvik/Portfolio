from flask import Flask, render_template, request, redirect, url_for, session, flash
from firebase import firebase
from functools import wraps
from flask import make_response

app = Flask(__name__)
app.secret_key = '*John3211#*John3211#*John3211#*John3211#*John3211#'

fb = firebase.FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/',None)

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get('admin_logged_in'):
#             return redirect(url_for('admin_login'))
#         return f(*args, **kwargs)
#     return decorated_function



def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache

@app.route('/admin-login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        links = fb.get('/links/-OOvwHeVJtSsrjh3QnWR/links', None)
        stored_username = links.get('admin_username')
        stored_password = links.get('admin_password')

        if username == stored_username and password == stored_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_intro'))
        else:
            flash("Invalid username or password.")
            return render_template('admin-login.html')
    
    return render_template('admin-login.html')



@app.route('/admin-home', methods=['GET', 'POST'])
@nocache
def admin_intro():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        form = request.form
        if 'new_skill' in form:
            new_skill = form['new_skill'].strip()
            if new_skill:
                raw = fb.get('/landing/skills-list', None) or {}
                if raw:
                    key = next(iter(raw))
                    skills = raw[key].get('skills', [])
                    skills.append(new_skill)
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
                else:
                    fb.post('/landing/skills-list', {'skills': [new_skill]})
        elif 'edited_skill' in form:
            idx = int(form['edit_index'])
            edited = form['edited_skill'].strip()
            raw = fb.get('/landing/skills-list', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills[idx] = edited
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
        elif 'delete_index' in form:
            idx = int(form['delete_index'])
            raw = fb.get('/landing/skills-list', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
        elif 'edited_bio' in form:
            new_bio = form['edited_bio'].strip()
            if new_bio:
                raw_bio = fb.get('/landing/bio', None) or {}
                if raw_bio:
                    bio_key = next(iter(raw_bio))
                    fb.put(f'/landing/bio/{bio_key}', 'bio', new_bio)
                else:
                    fb.post('/landing/bio', {'bio': new_bio})
        return redirect(url_for('admin_intro'))

    raw = fb.get('/landing/skills-list', None) or {}
    skills = []
    for block in raw.values():
        skills.extend(block.get('skills', []))

    raw_bio = fb.get('/landing/bio', None) or {}
    bio = next(iter(raw_bio.values())).get('bio', '') if raw_bio else ''

    return render_template('admin-home.html', skills=skills, bio=bio)



@app.route('/admin-about', methods=['GET', 'POST'])
def admin_about():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if 'new_title' in request.form:
        title = request.form['new_title'].strip()
        desc = request.form['new_description'].strip()
        pct = int(request.form['new_percentage'])
        if title and desc and 0 <= pct <= 100:
            raw = fb.get('/about/skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                skills.append({
                    'Skill': title,
                    'Description': desc,
                    'percentage': pct
                })
                fb.put(f'/about/skills/{key}', 'skills', skills)
            else:
                fb.post('/about/skills', {
                    'skills': [{
                        'Skill': title,
                        'Description': desc,
                        'percentage': pct
                    }]
                })

    elif request.method == 'POST':
        if 'edited_bio_heading' in request.form:
            new_heading = request.form['edited_bio_heading'].strip()
            raw_head = fb.get('/about/heading', None) or {}
            if raw_head:
                key = next(iter(raw_head))
                fb.put(f'/about/heading/{key}', 'heading', new_heading)
            else:
                fb.post('/about/heading', {'heading': new_heading})

        elif 'edited_bio' in request.form:
            new_bio = request.form['edited_bio'].strip()
            raw = fb.get('/about/bio', None) or {}
            if raw:
                key = next(iter(raw))
                fb.put(f'/about/bio/{key}', 'bio', new_bio)
            else:
                fb.post('/about/bio', {'bio': new_bio})

        elif 'delete_index' in request.form:
            idx = int(request.form['delete_index'])
            raw = fb.get('/about/skills', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    fb.put(f'/about/skills/{key}', 'skills', skills)

        elif 'edited_skill' in request.form and 'edited_description' in request.form and 'edited_percentage' in request.form:
            idx   = int(request.form['edit_index'])
            title = request.form['edited_skill'].strip()
            desc  = request.form['edited_description'].strip()
            pct   = int(request.form['edited_percentage'])
            raw   = fb.get('/about/skills', None) or {}
            if raw:
                key    = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills[idx]['Skill']       = title
                    skills[idx]['Description'] = desc
                    skills[idx]['percentage']  = pct
                    fb.put(f'/about/skills/{key}', 'skills', skills)

        return redirect(url_for('admin_about'))

    raw_bio = fb.get('/about/bio', None) or {}
    bio = next(iter(raw_bio.values())).get('bio', '') if raw_bio else ''

    raw_head = fb.get('/about/heading', None) or {}
    heading = next(iter(raw_head.values())).get('heading', '') if raw_head else ''

    raw_skills = fb.get('/about/skills', None) or {}
    skills = []
    for block in raw_skills.values():
        skills.extend(block.get('skills', []))

    return render_template('admin-about.html', bio=bio, heading=heading, skills=skills)



@app.route('/admin-experience', methods=["GET", "POST"])
@nocache
def admin_experience():
    edit_data = None

    if request.method == "POST":
        # Handle Edit request
        if 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get(f'/experience/{key}', None)
            edit_data['key'] = key  # Include the key for the update
        # Handle Update submission
        elif 'update_key' in request.form:
            key = request.form['update_key']
            updated = {
                "company": request.form['company'],
                "role": request.form['role'],
                "duration": request.form['duration'],
                "description": request.form['description']
            }
            fb.put('/experience', key, updated)
            return redirect(url_for('admin_experience'))
        # Handle Add new
        else:
            company = request.form.get("company")
            role = request.form.get("role")
            duration = request.form.get("duration")
            description = request.form.get("description")
            if company and role and duration and description:
                fb.post('/experience', {
                    "company": company,
                    "role": role,
                    "duration": duration,
                    "description": description
                })
            return redirect(url_for('admin_experience'))

    experiences = fb.get('/experience', None) or {}
    return render_template('admin-experience.html', experiences=experiences, edit_data=edit_data)


@app.route('/delete-experience', methods=['POST'])
@nocache
def delete_experience():
    key = request.form.get('key')
    if key:
        fb.delete('/experience', key)
    return redirect(url_for('admin_experience'))



@app.route('/admin-education', methods=["GET", "POST"])
@nocache
def admin_education():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    edit_data = None
    if request.method == "POST":
        # Edit button clicked
        if 'edit_key' in request.form:
            key = request.form['edit_key']
            edit_data = fb.get(f'/resume/education/{key}', None)
            if edit_data:
                edit_data['key'] = key

        # Update button submitted
        elif 'update_key' in request.form:
            key = request.form['update_key']
            updated = {
                "institution": request.form['institution'],
                "designation": request.form['designation'],
                "period": request.form['period'],
                "description": request.form['description']
            }
            fb.put('/resume/education', key, updated)
            return redirect(url_for('admin_education'))

        # Add new entry
        else:
            institution = request.form.get("institution")
            designation = request.form.get("designation")
            period = request.form.get("period")
            description = request.form.get("description")

            if institution and designation and period and description:
                fb.post('/resume/education', {
                    "institution": institution,
                    "designation": designation,
                    "period": period,
                    "description": description
                })

            return redirect(url_for('admin_education'))

    education = fb.get('/resume/education', None) or {}
    return render_template(
        'admin-education.html',
        education=education,
        edit_data=edit_data
    )


@app.route('/delete-education', methods=["POST"])
@nocache
def delete_education():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    key = request.form.get('key')
    if key:
        fb.delete('/resume/education', key)
    return redirect(url_for('admin_education'))


@app.route('/admin-contact', methods=["GET", "POST"])
@nocache
def admin_contact():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin-contact.html')



@app.route('/logout')
def admin_logout():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    session.clear()
    return redirect('admin-login')

@app.route('/')
def index():
    return redirect(url_for('admin_login')) 

if __name__ == "__main__":
    app.run(port=5001)

