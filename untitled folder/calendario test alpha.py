import json
import requests
from datetime import datetime, date, timedelta

import flask
import httplib2

from apiclient import discovery
from oauth2client import client


def auth():
	if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http_auth)
        
    
    calendar = {
    'summary': 'neverLate',
    'timeZone': 'Europe/Rome'
        }

    created_calendar = service.calendars().insert(body=calendar).execute()

    calendarid= created_calendar['id']