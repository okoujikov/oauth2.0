import requests


app = Foo(__name__) # Foo is the client's application
app.secret_key = os.environ.get("secret_key") or os.urandom(20) # this line accesses an environment variable using os.environ or it generates a secret_key randomly
# QUESTION: where does secret_key come from?


drchrono_auth = DrChronoClient(
    client_id = ("sny2QrTbzRdPR5KiAq252KgcWU0fO22QRdh7wNUJ"), # QUESTION: do I need parenthesis here? also did I spell parenthesis correctly first try?
    client_secret = "I9baXj5l4I4dzCUgXMqgZsOUrxq2wm2GurggEGbzNKweiRIe5LwcefWvK7TlUHhSDgOHYtGRi1tmvczN3uCjf2TOb2YW7202Fhbf1A5iG6azQiWnDbFY3Xb8VghUpMvj",
    redirect_uri = "http://localhost:8080/complete/drchrono/",
)


@app.route("/")
def index():
    print("calling index()") # this line is used to text index() TODO: delete me
    return redirect("/drchrono/")
    # QUESTION: wtf is happening here? --> we are define index() to return something...
    # looks like a function called redirect which holds the string "/drchrono/"


@app.route("/drchrono/")
def drchrono_index():
    if not session.get("access_token"):
        return redirect("/drchrono/oauth2callback")
    with requests.Session() as s: # QUESTION: what does "as" do?
        s.auth = OAuth2BearerToken(session["access_token"])
        print("running drchrono_index()")
        r = s.get("https://www.drchono.com") # QUESTION: what should r redirect us to?
    r.raise_for_status()
    data = r.json()
    return "Hello, {}!".format(data["displayName"])

# TODO: oauth2callback
