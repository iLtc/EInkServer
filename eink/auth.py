from flask import Blueprint, current_app, request, url_for, session, redirect
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/google')
def google():
    account = request.args.get('account', '')
    if account == '':
        return {
            'status': 'fail',
            'reason': 'Miss account name'
        }, 404

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

            return {
                'status': 'success',
                'message': 'Credentials for {} have been refreshed!'.format(account)
            }

        else:
            client_secrets_file = '{}/{}'.format(current_app.instance_path, 'client_secret.json')
            flow = Flow.from_client_secrets_file(client_secrets_file, scopes=current_app.config['GOOGLE_AUTH_SCOPES'])
            flow.redirect_uri = url_for('auth.google_callback', _external=True)

            authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
            session['state'] = state
            session['google_account'] = account

            return redirect(authorization_url)

    return {
        'status': 'success',
        'message': 'Credentials for {} are fine!'.format(account)
    }


@bp.route('/google_callback')
def google_callback():
    state = session['state']
    account = session['google_account']

    client_secrets_file = '{}/{}'.format(current_app.instance_path, 'client_secret.json')
    flow = Flow.from_client_secrets_file(client_secrets_file, scopes=current_app.config['GOOGLE_AUTH_SCOPES'], state=state)
    flow.redirect_uri = url_for('auth.google_callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials

    pickle_name = '{}/{}.pickle'.format(current_app.instance_path, account)

    with open(pickle_name, 'wb') as token:
        pickle.dump(creds, token)

    return {
        'status': 'success',
        'message': 'Credentials for {} have been saved!'.format(account)
    }
