import os
import datetime

from services import DrChronoClient
from apiEndpoints import AppointmentEndpoint
from flask import Flask, request, redirect, session

drchrono_auth = DrChronoClient( # drchrono_auth is used to pass in client_id, client_secret, redirect_uri.
    # These values can be entered manually below or through the terminal for privacy/security.
    # How it's currently set up, these values need to be passed in with export statements.
    # client_id and client_secret are given to the developer by drchrono on the drchrono website under Account > API
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    # redirect_uri is chosen by the developer and configured in the drchrono website under Account > API
    redirect_uri = "http://localhost:5000/drchrono/oauth2callback",
)

app = Flask(__name__) # initialize the Flask framework

app.config['SECRET_KEY'] = os.urandom(32) # set the secret key to a random 32-character string

@app.route("/") # redirects the user to http://localhost:5000/drchrono/
def index():
    return redirect("/drchrono/")

@app.route("/drchrono/") # checks for an access token and uses it to return data from the appointments endpoint
def drchrono_index():
    if not session.get("access_token"):
        # if there is no access token then client is redirected to http://localhost:5000/drchrono/drchrono/login
        return redirect("/drchrono/login")
    # if the access token is available, we use it to access the Appointment Endpoint
    api = AppointmentEndpoint(session.get('access_token')) # api is set to the appointment endpoint using the access token
    date = datetime.date.today() # gets the current date
    data = api.list(date=date) # gets a list of appointments using the date as a keyword argument
    return str(list(data)) # returns appointment data from the given date

@app.route("/drchrono/login") # start the login process
def drchrono_login():
    return redirect(drchrono_auth.authorize_url(
        scope=["calendar:read", "clinical:read"],  # these scope parameters are required to view appointments
        response_type="code",
    ))

@app.route("/drchrono/oauth2callback") # finish the login process
def drchrono_oauth2callback():
    # check for errors and prints a friendly error message if true
    error = request.args.get("error")
    if error:
        return "error :( {!r}".format(error) # prints error if there is one
    # request to get a code from the DrChrono generated url for temporary use
    code = request.args.get("code")
    if not code: # if there is no code go back to the login process
        return redirect("/drchrono/login")
    # use the temporary code to get a semi-perminent access token
    data = drchrono_auth.get_token(
        code=code,
        grant_type="authorization_code", # describes code type - https://oauth.net/2/grant-types/authorization-code/
    )
    session["access_token"] = data.get("access_token") # sets session["access_token"] equal to a token
    return redirect("/")

@app.route("/drchrono/showtoken") # route to show a token
def drchrono_showtoken():
    token = session.get("access_token")
    return token

@app.route("/drchrono/logout") # route to logout of drchrono
def drchrono_logout():
    del session["access_token"]
    return "Congratulations your token has been removed"

if __name__ == "__main__":
    app.run(debug=True)
