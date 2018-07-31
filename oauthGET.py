import requests
import os
import jwt
import datetime


from services import DrChronoClient
from requests_oauth2 import OAuth2BearerToken
from flask import Flask, jsonify, make_response, request, redirect, session
from functools import wraps # used for protected and unprotected routes
from apiEndpoints import AppointmentEndpoint

app = Flask(__name__) # initialize Flask
# app.secret_key = os.environ.get("secret_key") or os.urandom(20) # this is the secret key for your flask webserver
# this line accesses an environment variable using os.environ or it generates a secret_key randomly
# Q: where does secret_key come from? --> A: we are generating it with os.urandom(20)
# For more info: http://flask.pocoo.org/docs/1.0/quickstart/#sessions


drchrono_auth = DrChronoClient( # passing in client_id, client_secret, redirect_uri
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    redirect_uri = "http://localhost:5000/drchrono/oauth2callback",
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
    return jsonify({'message' : "This is only available for people with valid tokens."})

@app.route("/")
def index():
    return redirect("/drchrono/") #this was /drchrono/

@app.route("/login") # get login information for authorization
def login():

    auth = request.authorization

    if auth and auth.password =="debuger":
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY']) # creates an app token for the user (goal is to get a user token back)
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response("Could not verify!", 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

@app.route("/drchrono/")
def drchrono_index():
    if not session.get("access_token"):
        return redirect("/drchrono/oauth2callback") # TODO: redirect to DrChrono login
    api = AppointmentEndpoint(session.get('access_token'))
    data = api.list(date="2018-07-20")
    return str(list(data))

@app.route("/drchrono/oauth2callback")
def google_oauth2callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return "error :( {!r}".format(error)
    if not code:
        return redirect(drchrono_auth.authorize_url(
            scope=["profile", "email"],
            response_type="code",
        ))
    data = drchrono_auth.get_token(
        code=code,
        grant_type="authorization_code",
    )
    session["access_token"] = data.get("access_token")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
