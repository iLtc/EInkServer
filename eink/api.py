from flask import Blueprint, current_app, request
import requests

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
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']

    events = []

    return ''
