from requests_oauth2 import OAuth2

class DrChronoClient(OAuth2):
    # TODO: search API documentation to find this stuff. DONE
    # TODO: confirm that this is the correct documentation and it works
    site = "https://drchrono.com"
    authorization_url = "/o/authorize"
    token_url = "/o/token/"
    scope_sep = " "
