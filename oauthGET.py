import requests
import os
import jwt
import datetime
# QUESTION: would it be best to design this program for python or python3? Assuming python would be more accessible for users --> Answer: python3 might be best

from services import DrChronoClient
from requests_oauth2 import OAuth2BearerToken
from flask import Flask, jsonify, make_response, request, redirect, session
from functools import wraps # used for protected and unprotected routes

app = Flask(__name__) # Placeholder for the oauthGET.py module. QUESTION: generally what is a placeholder??
app.secret_key = os.environ.get("secret_key") or os.urandom(20) # this is the secret key for your flask webserver
# this line accesses an environment variable using os.environ or it generates a secret_key randomly
# Q: where does secret_key come from? --> A: we are generating it with os.urandom(20)
# For more info: http://flask.pocoo.org/docs/1.0/quickstart/#sessions


drchrono_auth = DrChronoClient( # passing in client_id, client_secret, redirect_uri
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    redirect_uri = "http://localhost:8080/complete/drchrono/",
)

app.config['SECRET_KEY'] = 'thisisthesecretkey' # this is the secret key for now

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') #http://127.0.0.1:5000/route?token=asefjkldsasdfkljaskdfj

        if not token:
            return jsonify({'message' : "Token is missing!"}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : "Token is invalid!"}), 403

        return f(*args, **kwargs)
    return decorated

# QUESTION: Do I need unprotected and protected routes? Or will everything be protected?
@app.route('/unprotected')
def unprotected():
    return jsonify({'message' : "Anyone can view this!"})

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : "This is only available for people with a valid token."})

@app.route("/")
def index():
    return redirect("/login") #this was /drchrono/

@app.route("/login") # get login information for authorization
def login():
    auth = request.authorization

    if auth and auth.password =="password":
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY']) # creates a token for the user
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response("Could not verify!", 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

@app.route("/drchrono/")
def drchrono_index():
    if not session.get("access_token"):
        return redirect("/drchrono/oauth2callback") # TODO: redirect to DrChrono login
    with requests.Session() as s: # QUESTION: what does "as" do?
        s.auth = OAuth2BearerToken(session["access_token"])
        print("running drchrono_index()")
        r = s.get("https://www.drchono.com") # QUESTION: what should r redirect us to?
    r.raise_for_status()
    data = r.json()
    return "Hello, {}!".format(data["displayName"])

# TODO: oauth2callback

if __name__ == "__main__":
    app.run(debug=True)
