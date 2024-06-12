import base64
import os
from urllib import response
from urllib.parse import urlencode
from flask import Flask, abort, json, jsonify, redirect, render_template, request, send_file, send_from_directory, session
# from flask_jwt_extended import *
import markdown
import pymysql
import pymysql.cursors
import requests
from config.config import Config, DB_Config, Google_Config, Kakao_Config, Naver_Config
from secure.account_secure import AccountSecurity
from firebase_admin import credentials, messaging
import firebase_admin

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES

# Setup Oauth
app.config['GOOGLE_OAUTH2_CLIENT_SECRETS_FILE'] = './config/google_client_secrets.json'
app.config['GOOGLE_CLIENT_ID'] = Google_Config.GOOGLE_CLIENT_ID
app.config['GOOGLE_CLIENT_SECRET'] = Google_Config.GOOGLE_CLIENT_SECRET
app.config['GOOGLE_REDIRECT_URI'] = Google_Config.GOOGLE_REDIRECT_URI
app.config['GOOGLE_SCOPE'] = Google_Config.GOOGLE_SCOPE
app.config['GOOGLE_AUTHORIZE_ENDPOINT'] = Google_Config.GOOGLE_AUTHORIZE_ENDPOINT
app.config['GOOGLE_TOKEN_ENDPOINT'] = Google_Config.GOOGLE_TOKEN_ENDPOINT
app.config['GOOGLE_RESOURCE_ENDPOINT'] = Google_Config.GOOGLE_RESOURCE_ENDPOINT

app.config['KAKAO_CLIENT_ID'] = Kakao_Config.KAKAO_CLIENT_ID
app.config['KAKAO_CLIENT_SECRET'] = Kakao_Config.KAKAO_CLIENT_SECRET
app.config['KAKAO_REDIRECT_URI'] = Kakao_Config.KAKAO_REDIRECT_URI
app.config['KAKAO_AUTHORIZE_ENDPOINT'] = Kakao_Config.KAKAO_AUTHORIZE_ENDPOINT
app.config['KAKAO_TOKEN_ENDPOINT'] = Kakao_Config.KAKAO_TOKEN_ENDPOINT
app.config['KAKAO_RESOURCE_ENDPOINT'] = Kakao_Config.KAKAO_RESOURCE_ENDPOINT

app.config['NAVER_CLIENT_ID'] = Naver_Config.NAVER_CLIENT_ID
app.config['NAVER_CLIENT_SECRET'] = Naver_Config.NAVER_CLIENT_SECRET
app.config['NAVER_REDIRECT_URI'] = Naver_Config.NAVER_REDIRECT_URI
app.config['NAVER_AUTHORIZE_ENDPOINT'] = Naver_Config.NAVER_AUTHORIZE_ENDPOINT
app.config['NAVER_TOKEN_ENDPOINT'] = Naver_Config.NAVER_TOKEN_ENDPOINT
app.config['NAVER_RESOURCE_ENDPOINT'] = Naver_Config.NAVER_RESOURCE_ENDPOINT


app.config['SECRET_KEY'] = Config.SECRET_KEY

# Setup Firebase
cred = credentials.Certificate('./config/firebaseServiceAccountKey.json')
firebase_admin.initialize_app(
    cred)

# Setup Database
app.config['SQLALCHEMY_DATABASE_URI'] = DB_Config.DB_URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = pymysql.connect(
    host=DB_Config.host,
    user=DB_Config.user,
    password=DB_Config.password,
    charset=DB_Config.charset,
    database=DB_Config.database,
)
cursor = db.cursor(pymysql.cursors.DictCursor)

# jwt = JWTManager(app)

deviceToken = {}


@app.route('/regist/token', methods=['POST'])
def registToken():
    if request.is_json:
        data = request.get_json()
        device_name = data['device_name']
        device_token = data['device_token']
        deviceToken[device_name] = device_token
        print(deviceToken)
        return jsonify({"msg": 'Regist Success'}), 200
    else:
        return jsonify({"msg": 'Incorrect Data Type'}), 400


@app.route('/test/notify', methods=['GET'])
def mesgSend():
    device_name = request.args.get("device_name")
    registration_token = deviceToken[device_name]
    message = messaging.Message(
        notification=messaging.Notification(
            title='Notification Occurred',
            body='This notification is a test notification.'
        ),
        token=registration_token,
    )
    response = messaging.send(message)
    print('Successfully sent message:', response)
    return jsonify({"msg": "Success"}), 200


@app.route('/login/authorize/<target>', methods=['GET'])
def authorize(target):
    if target not in ['google', 'kakao', 'naver']:
        return abort(404)
    target = target.upper()
    # 공통 변수
    authorize_endpoint = app.config.get(f'{target}_AUTHORIZE_ENDPOINT')
    client_id = app.config.get(f'{target}_CLIENT_ID')
    redirect_uri = app.config.get(f'{target}_REDIRECT_URI')
    response_type = "code"
    scope = app.config.get(f'{target}_SCOPE')

    if target == 'GOOGLE':
        query_string = urlencode(dict(
            redirect_uri=redirect_uri,
            client_id=client_id,
            scope=scope,
            response_type=response_type
        ))
        authorize_redirect = f'{authorize_endpoint}?{query_string}'
    elif target == 'KAKAO':
        query_string = urlencode(dict(
            redirect_uri=redirect_uri,
            client_id=client_id,
            response_type=response_type
        ))
        authorize_redirect = f'{authorize_endpoint}?{query_string}'
    elif target == 'NAVER':
        state = 'test'
        query_string = urlencode(dict(
            redirect_uri=redirect_uri,
            client_id=client_id,
            response_type=response_type,
            state=state,
        ))
        authorize_redirect = f'{authorize_endpoint}?{query_string}'
    try:
        return redirect(authorize_redirect)
    except:
        return abort(404)


@app.route('/callback/<platform>')
def oauthCallback(platform):
    platform = platform.upper()
    token_endpoint = app.config.get(f'{platform}_TOKEN_ENDPOINT')
    resource_endpoint = app.config.get(f'{platform}_RESOURCE_ENDPOINT')
    client_id = app.config.get(f'{platform}_CLIENT_ID')
    client_secret = app.config.get(f'{platform}_CLIENT_SECRET')
    redirect_uri = app.config.get(f'{platform}_REDIRECT_URI')
    code = request.args.get('code')
    state = request.args.get('state')
    grant_type = 'authorization_code'

    resp = requests.post(token_endpoint, data=dict(  # type: ignore
        code=code,
        client_id=client_id,
        client_secret=client_secret,
        state=state,
        redirect_uri=redirect_uri,
        grant_type=grant_type
    ))

    resp = resp.json()
    access_token = resp['access_token']
    # id_token = resp['id_token']
    headers = {
        'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request(
        "GET", resource_endpoint, headers=headers)  # type: ignore
    if platform == 'NAVER':
        user_info = response.json()['response']
        social_uuid = user_info['id']
        user_email = user_info['email']
        user_name = user_info['name']
        sql = f"select user_name from user where user_id = '{user_email}'"
    elif platform == 'KAKAO':
        user_info = response.json()
        social_uuid = user_info['id']
        user_email = user_info['kakao_account']['email']
        user_name = user_info['kakao_account']['profile']['nickname']
    elif platform == 'GOOGLE':
        user_info = response.json()
        social_uuid = user_info['sub']
        user_email = user_info['email']
        user_name = user_info['name']

    sql = f"select user_name from user where user_id = '{user_email}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    if (len(result) == 0):
        signup(user_email, user_name, platform, social_uuid=social_uuid)
        return 'now signup!'
    else:
        return 'login success'


def signup(user_id, user_name, social_platform, social_uuid):
    signup_sql = f"insert into user(user_id, user_name, social_platform, social_uuid) values ('{user_id}', '{user_name}', '{social_platform}',  '{social_uuid}')"
    cursor.execute(signup_sql)
    db.commit()


@app.route('/app/register/<platform>')
def app_register(platform):
    platform = platform.upper()
    if request.is_json:
        req = request.get_json()
        register_sql = f"insert into user(user_id, user_name, social_platform, social_uuid) values ('{req['user_id']}', '{req['user_name']}', '{platform}', '{req['social_uuid']}')"
        try:
            cursor.execute(register_sql)
            db.commit()
        except:
            return jsonify({"msg": 'Error Ocurred'}), 400
        return jsonify({"msg": 'Register Success'}), 200
    return jsonify({"msg": 'Uncorrect Data Type'}), 400


@app.route('/app/auth/<platform>', methods=['POST'])
def app_login(platform):
    platform = platform.upper()
    if request.is_json:
        req = request.get_json()
        user_id = req['user_id']
        social_uuid = req['social_uuid']
        sql = f"select * from user where user_id = '{user_id}'"
        cursor.execute(sql)
        db_result = cursor.fetchone()
        if db_result is not None:
            if db_result['social_platform'] == platform:
                if db_result['social_uuid'] == social_uuid:
                    return jsonify({"msg": f'{user_id} matched'}), 200
                else:
                    return f"{social_uuid} is not match {db_result['social_uuid']}"
            else:
                return f"Already Signup"
    return '123'


@app.route('/test/notification', methods=['POST'])
def notificationTest():
    if request.is_json:
        data = request.get_json()
        obj = data['object']
    else:
        obj = 1
    registration_token = 'Please REENTER TOKEN'
    message = messaging.Message(
        notification=messaging.Notification(
            title='Event Occurred',
            body=f'{obj} is Detected'
        ),
        token=registration_token,
    )
    response = messaging.send(message)
    print('Successfully sent message:', response)
    return '1'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# @app.route('/favicon.ico')
# def favicon():
#     favicon_path = app.root_path + '/favicon.ico'
#     if os.path.exists(favicon_path):
#         return send_file(favicon_path)
#     else:
#         return 404
# @app.route('/auth', methods=['POST'])
# def login():
#     if not request.is_json:
#         return jsonify({"msg": "Missing JSON in request"}), 400
#     user_id = request.json.get('userid')
#     password = request.json.get('passwd')

#     if session['public_key'] != None:
#         print('Has Public Key')

#     if not user_id:
#         return jsonify({"msg": "Missing username parameter"})
#     elif not password:
#         return jsonify({"msg": "Missing password parameter"})

#     cursor.execute(
#         f'''
#         select user_pwd from user where user_id = '{user_id}'
#         '''
#     )
#     result = cursor.fetchone()
#     if result is not None:
#         if result['user_pwd'] == password:
#             # Identity can be any data that is json serializable
#             access_token = create_access_token(identity=user_id)
#             refresh_token = create_refresh_token(identity=user_id)
#             return jsonify({'msg': 'Login Done','access_token':access_token, 'refresh_token': refresh_token}), 200
#     return jsonify({"msg": "Check User ID or Password"})

# @app.route('/get/key', methods=['POST'])
# def returnKey():
#     priKey, pubKey = AccountSecurity.generate_keys()
#     session['public_key'] =pubKey
#     print(pubKey)
#     return json.dumps({'msg': 'Just test', 'public_key': pubKey}, default=str,), 200

# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     # Access the identity of the current user with get_jwt_identity
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200


# @app.route('/refresh', methods=['GET'])
# @jwt_required(refresh=True)
# def refresh():
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity=current_user)
#     return jsonify(access_token = access_token, current_user=current_user)

if __name__ == '__main__':
    app.run(host=Config.host, port=Config.port, debug=Config.DEBUG,)
    db.close()
