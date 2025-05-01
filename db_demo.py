from firebase import firebase
fb = firebase.FirebaseApplication('https://portfolio-536e2-default-rtdb.firebaseio.com/',None)


data= {

}

resp = fb.get('/landing/bio', "-OOvfwd4lcYOwXVhzRGL")['bio']
print(resp["bio"])


"""
data= {
    "intro-skills": ["An AWS Solutions Architect", "A Data Analyst", "A Web Developer"]
    }

resp = fb.get('/admin-creds', "-OOvG_s55K4v1KcUv5mL")
print(resp)

"""