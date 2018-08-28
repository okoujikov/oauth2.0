from requests_oauth2 import OAuth2

# add a new class called DrChronoClient which is based on the requests_oauth2 library
class DrChronoClient(OAuth2):
    site = "https://drchrono.com"
    authorization_url = "/o/authorize"
    token_url = "/o/token/"
    scope_sep = " "
