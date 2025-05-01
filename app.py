from flask import Flask,render_template,request, redirect, url_for
from firebase import firebase

fb = firebase.FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/',None)
app = Flask(__name__)

@app.route('/')
def home():

    landing_data = fb.get('/landing', None)
    about_data = fb.get('/about', None)
    resume_data = fb.get('/resume', None)
    links = fb.get(f'https://portfolio-536e2-default-rtdb.firebaseio.com/links/-OOvwHeVJtSsrjh3QnWR/links', None)

    #get landing data
    # ─── Flatten your skills array ───
    raw_skills = landing_data.get('skills-list', {})
    skills = []
    for block in raw_skills.values():
        skills.extend(block.get('skills', []))

    # ─── extract bio ───
    raw_bio = landing_data.get('bio', {})
    bio = ''
    if raw_bio:
        bio = next(iter(raw_bio.values())).get('bio', '')
        #print(bio)

    #get about data
    # ─── About node ───
    about = fb.get('/about', None) or {}

    # About heading & paragraph (if you need them)
    raw_heading = about.get('heading', {})
    about_heading = (
        next(iter(raw_heading.values())).get('heading', '')
        if raw_heading else ''
    )

    raw_abio = about.get('bio', {})
    about_paragraph = (
        next(iter(raw_abio.values())).get('bio', '')
        if raw_abio else ''
    )
    about_skills = []
    for block in about.get('skills', {}).values():
        about_skills.extend(block.get('skills', []))


    #get resume_data


    #get links
    admin_password = links.get('admin_password')
    admin_username = links.get('admin_username')
    email = links.get('email')
    linkedin = links.get('linkedin')
    phone = links.get('phone')
    resume = links.get('resume')
    telegram = links.get('telegram')

    return render_template('index.html', skills=skills, bio=bio, about_skills = about_skills)


@app.route('/contact',methods=["GET","POST"])
def contact():
    if request.method=="POST":
        name=request.form.get('name')
        cli_email=request.form.get('email')
        sub=request.form.get('subject')
        message=request.form.get('message')
        #print(name,cli_email,sub,message)zd
        return "OK"


@app.route('/admin-login', methods=["GET","POST"])
def admin_login():
    return render_template('/admin-module/admin-login.html')


@app.route('/admin-home', methods=['GET','POST'])
def admin_intro():
    if request.method == 'POST':
        form = request.form

        # ---- 1) New Skill logic ----
        if 'new_skill' in form:
            new_skill = form['new_skill'].strip()
            #print("🔔 Adding new skill:", new_skill)   # debug – watch your console!
            if new_skill:
                raw = fb.get('/landing/skills-list', None) or {}
                if raw:
                    key = next(iter(raw))
                    skills = raw[key].get('skills', [])
                    skills.append(new_skill)
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)
                else:
                    fb.post('/landing/skills-list', {'skills': [new_skill]})

        # ---- 2) Update Skill logic ----
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

        # ---- 3) Delete Skill logic ----
        elif 'delete_index' in form:
            idx = int(form['delete_index'])
            raw = fb.get('/landing/skills-list', None) or {}
            if raw:
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    skills.pop(idx)
                    fb.put(f'/landing/skills-list/{key}', 'skills', skills)

        # ——— 4) Update Bio ———
        elif 'edited_bio' in form:
            new_bio = form['edited_bio'].strip()
            if new_bio:
                # fetch the one bio block
                raw_bio = fb.get('/landing/bio', None) or {}
                if raw_bio:
                    bio_key = next(iter(raw_bio))
                    # overwrite its "bio" field
                    fb.put(f'/landing/bio/{bio_key}', 'bio', new_bio)
                else:
                    # no bio yet? create one
                    fb.post('/landing/bio', {'bio': new_bio})

        return redirect(url_for('admin_intro'))

    # GET → fetch & flatten skills
    raw = fb.get('/landing/skills-list', None) or {}
    skills = []
    for block in raw.values():
        skills.extend(block.get('skills', []))

    # bio:
    raw_bio = fb.get('/landing/bio', None) or {}
    bio = ''
    if raw_bio:
        # get the first block’s "bio" value
        bio = next(iter(raw_bio.values())).get('bio', '')
    return render_template(
        'admin-module/admin-home.html',
        skills=skills, bio=bio
    )


@app.route('/admin-about', methods=['GET','POST'])
def admin_about():
    # ——— 1) Add New Skill ———
    if 'new_title' in request.form:
        # grab the inputs
        title = request.form['new_title'].strip()
        desc = request.form['new_description'].strip()
        pct = int(request.form['new_percentage'])
        if title and desc and 0 <= pct <= 100:
            # fetch or create the skills node
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
        # —— Save updated Bio Heading ——
        if 'edited_bio_heading' in request.form:
            new_heading = request.form['edited_bio_heading'].strip()
            raw_head = fb.get('/about/heading', None) or {}
            if raw_head:
                # overwrite the existing heading node
                key = next(iter(raw_head))
                fb.put(f'/about/heading/{key}', 'heading', new_heading)
            else:
                # create a new heading node if none exists
                fb.post('/about/heading', {'heading': new_heading})

        # —— Save updated Bio paragraph ——
        elif 'edited_bio' in request.form:
            new_bio = request.form['edited_bio'].strip()
            raw = fb.get('/about/bio', None) or {}
            if raw:
                key = next(iter(raw))
                fb.put(f'/about/bio/{key}', 'bio', new_bio)
            else:
                fb.post('/about/bio', {'bio': new_bio})

        # ——— Delete an About‐Skill ———
        elif 'delete_index' in request.form:
            idx = int(request.form['delete_index'])
            raw = fb.get('/about/skills', None) or {}
            if raw:
                # get the one push‐key under /about/skills
                key = next(iter(raw))
                skills = raw[key].get('skills', [])
                if 0 <= idx < len(skills):
                    # remove that index
                    skills.pop(idx)
                    # write back the updated array
                    fb.put(f'/about/skills/{key}', 'skills', skills)

        # ——— Update an About-Skill ———
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

    # —— On GET, fetch bio, heading, and skills for rendering ——
    raw_bio = fb.get('/about/bio', None) or {}
    bio = next(iter(raw_bio.values())).get('bio', '') if raw_bio else ''

    raw_head = fb.get('/about/heading', None) or {}
    heading = next(iter(raw_head.values())).get('heading', '') if raw_head else ''

    raw_skills = fb.get('/about/skills', None) or {}
    skills = []
    for block in raw_skills.values():
        skills.extend(block.get('skills', []))

    return render_template(
        'admin-module/admin-about.html',
        bio=bio,
        heading=heading,
        skills=skills
    )


@app.route('/admin-experience', methods=["GET","POST"])
def admin_portal():
    return render_template('admin-module/admin-experience.html')


@app.route('/admin-education', methods=["GET","POST"])
def admin_education():
    return render_template('admin-module/admin-education.html')


@app.route('/admin-contact', methods=["GET","POST"])
def admin_contact():
    return render_template('admin-module/admin-contact.html')


@app.route('/logout')
def admin_logout():
    return redirect('/')

if __name__ == "__main__":
    app.run()

"""
4 sharpes -> 5000 (2500 per pair)
10 led -> 2000 (250 per light)
DJ sounds 1 Pin -> 11,000
   2 Pin -> 22,000

Artist -> 8,000
"""
