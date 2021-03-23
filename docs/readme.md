## Security

# User auth

* First pass simply uses cookie-based session auth, implemented via [Flask-Security](https://pythonhosted.org/Flask-Security/). In future better to move to JWT to scale more easily and allow mobile. This may require some refactoring of the `User` and `Role` relations in DB schema. See eg: [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/) or [this guide](https://realpython.com/token-based-authentication-with-flask/) for an intro into JWT-based auth.

# HTTPS

* No certification currently used. See [here](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) for info on how to serve Flask app over HTTPS.

# CSRF

* If roll a demo with cookie-based sessions then need to configure CSRF, as outlined [here](https://testdriven.io/blog/csrf-flask/).


