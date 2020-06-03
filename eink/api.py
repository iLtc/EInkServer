from flask import Blueprint, current_app, request
import requests
import os
import pickle
from google.auth.transport.requests import Request
import googleapiclient.discovery
import datetime
from pytz import timezone

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.before_request
def before_request():
    if request.path not in ['/api/status'] and request.args.get('token', '') != current_app.config['EINK_TOKEN']:
        return {
            'status': 'fail',
            'reason': 'Miss EINK Token'
        }, 403


@bp.route('/status')
def status():
    return {
        'status': 'success'
    }


@bp.route('/weather')
def weather():
    r = requests.get(
        'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=imperial&appid={}'.format(
            current_app.config['WEATHER_LAT'],
            current_app.config['WEATHER_LON'],
            current_app.config['OPENWEATHERMAP_APPID']
        ))

    if r.status_code == requests.codes.ok:
        data = r.json()

        results = {
            'status': 'success',
            'current': data['current'],
            'today': data['daily'][0],
            'tomorrow': data['daily'][1]
        }

    else:
        results = {
            'status': 'fail',
            'reason': 'HTTP Request Returns ' + str(r.status_code)
        }, r.status_code

    return results


@bp.route('/habitica')
def habitica():
    r = requests.get(
        'https://habitica.com/api/v3/tasks/user',
        headers={
            'x-api-user': current_app.config['HABITICA_USERID'],
            'x-api-key': current_app.config['HABITICA_TOKEN']
        }
    )

    if r.status_code == requests.codes.ok:
        data = r.json()

        results = {
            'status': 'success',
            'data': data['data']
        }

    else:
        results = {
            'status': 'fail',
            'reason': 'HTTP Request Returns ' + str(r.status_code)
        }, r.status_code

    return results


@bp.route('/calendar')
def calendar():
    events = []
    eastern = timezone('US/Eastern')
    now = datetime.datetime.now(eastern)

    for account, calendars in current_app.config['GOOGLE_CALENDARID_WITH_CREDENTIALS'].items():
        creds = None

        pickle_name = '{}/{}.pickle'.format(current_app.instance_path, account)

        if os.path.exists(pickle_name):
            with open(pickle_name, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

                with open(pickle_name, 'wb') as token:
                    pickle.dump(creds, token)

            else:
                return {
                    'status': 'failed',
                    'reason': '{} needs to be authenticated!'.format(account)
                }, 403

        calendar_service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)

        for name, calendar_data in calendars.items():
            data = calendar_service.events().list(
                calendarId=calendar_data['id'],
                orderBy='startTime',
                singleEvents=True,
                timeMin=now.isoformat(),
                timeMax=(now + datetime.timedelta(days=1)).isoformat()
            ).execute()

            for event in data['items']:
                event['calendar'] = name
                event['important'] = calendar_data['important']

                events.append(event)

    events.sort(key=lambda e: e['start']['dateTime'])

    return {
        'status': 'success',
        'events': events
    }
