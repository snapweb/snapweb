Snapweb: HTTP client for snapchat
=======================================

A web app and HTTP client for snapchat.

The web app supports logging in and viewing unread snapchats. Unlike the mobile
client, users can view snaps for as long as they like and/or save them.

Snapweb is a mostly  a frontend for pysnap (https://github.com/martinp/pysnap).
In addition to the web interface, some of the pysnap endpoints are exposed at
/api.

Endpoints:
```json
[
    "/api",
    "/get_updates",
    "/get_snaps",
    "/get_friends",
    "/get_best_friends",
    "/get_blocked"
]
```

An instance of the application is running at:
http://snapchat-web.heroku.com


Note: logging into the HTTP client will log the user out of the mobile client
as snapchat only allows a single client to be logged in at any time.

Setup
-----

    $ virtualenv ENV
    $ source ENV/bin/activate
    $ pip install -r requirements.txt
    $ python app.py


Requirements
-----
- Python 2.7
- Flask
- https://github.com/martinp/pysnap
- Twitter bootstrap
