from flask import Blueprint, current_app, request, send_file
import requests
import os
import pickle
from google.auth.transport.requests import Request
import googleapiclient.discovery
import datetime
from pytz import timezone, utc
from .models import db, Task
import json
from . import generator
import sys

bp = Blueprint('api', __name__, url_prefix='/api')

eastern = timezone('US/Eastern')


@bp.before_request
def before_request():
    if (current_app.config['ENV'] != 'development'
            and request.path not in ['/api/status']
            and request.args.get('token', '') != current_app.config['EINK_TOKEN']):
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
        old_data = r.json()['data']

        data = [{
            'type': temp['type'],
            'isDue': temp['isDue'],
            'completed': temp['completed'],
            'text': temp['text']
        } for temp in old_data if temp['type'] == 'daily']

        results = {
            'status': 'success',
            'data': data
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

            for temp in data['items']:
                events.append({
                    'calendar': name,
                    'important': calendar_data['important'],
                    'start': temp['start'],
                    'end': temp['end'],
                    'summary': temp['summary']
                })

    events.sort(key=lambda e: datetime.datetime.fromisoformat(e['start']['dateTime']).astimezone(eastern))

    return {
        'status': 'success',
        'events': events
    }


@bp.route('/omnifocus/update')
def omnifocus_update():
    data = request.args.get('data', '')

    if data == '':
        return {
                   'status': 'failed',
                   'reason': 'Miss data'
               }, 400

    try:
        data = json.loads(data)
    except:
        return {
                   'status': 'failed',
                   'reason': 'Update to load json data'
               }, 400

    # TODO: Remove deleted tasks

    for task in data:
        if task['dueDate']:
            task['dueDate'] = utc.localize(datetime.datetime.strptime(task['dueDate'], '%Y-%m-%dT%H:%M:%S.%fZ'))

        obj = Task.query.filter_by(task_id=task['task_id']).first()

        if obj:
            for key, val in task.items():
                if getattr(obj, key) != val:
                    setattr(obj, key, val)
        else:
            new_obj = Task(**task)

            db.session.add(new_obj)

    db.session.commit()

    return {'status': 'success'}


@bp.route('/omnifocus')
def omnifocus():
    now = datetime.datetime.now(eastern)
    today = eastern.localize(datetime.datetime(now.year, now.month, now.day, 23, 59, 59)).astimezone(utc)

    tasks = Task.query \
        .filter(Task.active == True, Task.completed == False, Task.taskStatus != 'Completed') \
        .filter(db.or_(Task.flagged == True, Task.inInbox == True, Task.dueDate <= today)).all()

    results = []

    for task in tasks:
        results.append(task.to_dict())

    results.sort(key=lambda e: e['dueDate'])

    return {
        'status': 'success',
        'tasks': results
    }


@bp.route('/trello')
def trello():
    cards = []

    for board_name, lists in current_app.config['TRELLO_LISTS'].items():
        for list_name, list_id in lists.items():
            r = requests.get(
                'https://api.trello.com/1/lists/{}/cards?key={}&token={}'.format(
                    list_id,
                    current_app.config['TRELLO_KEY'],
                    current_app.config['TRELLO_TOKEN']
                )
            )

            if r.status_code != requests.codes.ok:
                return {
                           'status': 'fail',
                           'reason': 'HTTP Request Returns ' + str(r.status_code)
                       }, r.status_code

            else:
                data = r.json()

                for item in data:
                    cards.append({
                        'name': item['name'],
                        'progress': '{}/{}'.format(item['badges']['checkItemsChecked'], item['badges']['checkItems']),
                        'list_name': list_name,
                        'board_name': board_name
                    })

    return {
        'status': 'success',
        'cards': cards
    }


@bp.route('/toggl')
def toggl():
    categories = {}

    for name, details in current_app.config['TOGGL_CATEGORIES'].items():
        categories[name] = {
            'pid': details['pid'] if 'pid' in details else [],
            'goal': details['goal'],
            'current': 0
        }

        if 'wid' in details and len(details['wid']) > 0:
            for wid in details['wid']:
                r = requests.get(
                    'https://www.toggl.com/api/v8/workspaces/{}/projects'.format(wid),
                    auth=(current_app.config['TOGGL_TOKEN'], 'api_token')
                )

                if r.status_code != requests.codes.ok:
                    return {
                               'status': 'fail',
                               'reason': 'HTTP Request Returns ' + str(r.status_code)
                           }, r.status_code

                categories[name]['pid'].extend([item['id'] for item in r.json()])

    now = datetime.datetime.now(eastern)
    start_date = eastern.localize(datetime.datetime(now.year, now.month, now.day, 0, 0, 0)).astimezone(utc)

    r = requests.get(
        'https://www.toggl.com/api/v8/time_entries',
        params={'start_date': start_date.isoformat()},
        auth=(current_app.config['TOGGL_TOKEN'], 'api_token')
    )

    if r.status_code != requests.codes.ok:
        return {
                   'status': 'fail',
                   'reason': 'HTTP Request Returns ' + str(r.status_code)
               }, r.status_code

    for time_entry in r.json():
        if 'stop' in time_entry:
            duration = time_entry['duration']
        else:
            start_time = datetime.datetime.fromisoformat(time_entry['start'])
            duration = int((now - start_time).total_seconds())

        for _, category in categories.items():
            if time_entry['pid'] in category['pid']:
                category['current'] += duration

    return {
        'status': 'success',
        'categories': categories
    }


@bp.route('/refresh')
def refresh():
    data_points = [
        {'name': 'weather', 'method': weather},
        {'name': 'habitica', 'method': habitica},
        {'name': 'calendar', 'method': calendar},
        {'name': 'omnifocus', 'method': omnifocus},
        {'name': 'trello', 'method': trello}
    ]

    data = {}

    for point in data_points:
        data[point['name']] = point['method']()

        if type(data[point['name']]) == tuple:
            return {
                       'status': 'failed',
                       'reason': 'Failed to get data from {}: {}'.format(point['name'],
                                                                         data[point['name']][0]['reason'])
                   }, 500

    try:
        generator.generator(data, current_app.root_path + '/')
    except:
        return {
                   'status': 'failed',
                   'reason': 'Failed to refresh: ' + str(sys.exc_info()[1])
               }, 500

    return {
        'status': 'success'
    }


@bp.route('/black.bmp')
@bp.route('/red.bmp')
@bp.route('/debug.bmp')
def static():
    return send_file(request.path.split('/')[2])
