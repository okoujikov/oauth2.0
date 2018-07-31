import os

from services import DrChronoClient
from apiEndpoints import AppointmentEndpoint
from flask import Flask, request, redirect, session

drchrono_auth = DrChronoClient( # drchrono_auth is used to pass in client_id, client_secret, redirect_uri.
    #  These values can be entered manually below or through the terminal for privacy/security. How it's currently set up, these values need to be passed in with export statements.
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    redirect_uri = "http://localhost:5000/drchrono/oauth2callback",
)

app = Flask(__name__) # initialize the Flask framework

app.config['SECRET_KEY'] = 'thisisthesecretkey'

@app.route("/")
def index():
    return redirect("/drchrono/") # redirects user to /drchrono/

@app.route("/drchrono/")
def drchrono_index():
    if not session.get("access_token"): # if there is no access token then client is redirected to /drchrono/oauth2callback
        return redirect("/drchrono/oauth2callback")
    api = AppointmentEndpoint(session.get('access_token')) # if there is an access token, we use it to access the Appointment Endpoint
    data = api.list(date="2018-07-20")
    return str(list(data)) # returns appointment data for 2018-07-20

@app.route("/drchrono/oauth2callback")
def drchrono_oauth2callback():
    code = request.args.get("code") # requests a code from DrChrono TODO: is this generated in the DrChrono server?
    error = request.args.get("error") # check for an error
    if error:
        return "error :( {!r}".format(error) # prints error if there is one TODO: can I get an error from this statement?
    if not code:
        return redirect(drchrono_auth.authorize_url( # if the variable code is empty, redirect and collect an access token TODO: verify
            scope=["calendar:read", "clinical:read"], # these parameters are required to view appointments
            response_type="code",
        ))
    data = drchrono_auth.get_token( # TODO: figure out what code and grant_type are ?
        code=code,
        grant_type="authorization_code",
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
    return "Congratulations logging out"

if __name__ == "__main__":
    app.run(debug=True)
