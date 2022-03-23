import logging

from google.oauth2 import id_token
from google.auth.transport import requests

from flask import Flask, request, session, redirect

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'F4Qjhgkjhgyfg8z\<sdnjj\xec]/'

@app.route('/', defaults={'filename': ''}, methods=['GET', 'POST'])
@app.route('/<path:filename>', methods=['GET', 'POST'])
def authz(filename):
    app.logger.debug(request.headers)
    app.logger.debug(request.form)
 
    # check if we get an callback from the OIDC auth flow
    #
    if filename.startswith("oauth/callback"):
        csrf_token_cookie = request.cookies.get('g_csrf_token')

        if not csrf_token_cookie:
            return 'No CSRF token in Cookie.', 400

        csrf_token_body = request.form.get('g_csrf_token')
        if not csrf_token_body:
           return 'No CSRF token in post body.', 400

        if csrf_token_cookie != csrf_token_body:
            return 'Failed to verify double submit cookie.', 400
        
        token = request.form.get('credential')
        client_id = request.form.get('clientid')

        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        
        session['id_token'] = token
        session['email'] = idinfo["email"]
        session['family_name'] = idinfo["family_name"]
        session['given_name'] = idinfo["given_name"]

        # TODO: redirect to the "ORIGIN-URL" instead of the "/" root path
        #
        return redirect("/home", code=302)

    # check user session and send HTTP-200 on success
    # TODO: check expirence time of the token. But right now the "session" has a livetime of only
    #       2 minutes and after this time period the id_token is gone.
    #
    if session.get('id_token'):
        print("Found user in session: "+session.get('email'))
        return "allow", 200, {
            "x-mail": session['email'],
            "x-family_name": session['family_name'],
            "x-given_name": session['given_name'],
            "x-role": "user"
        }
    else :
        print("No user in session: ")
        return "allow", 200, {
            "x-mail": "Guest",
            "x-family_name": "Guest",
            "x-given_name": "Guest",
            "x-role": "guest"
        }

if __name__ == '__main__':
    print("AuthZ Server Up and running")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=False)


