import json
import time
import datetime
import uuid
import hmac
import hashlib
import requests
import platform

import account_env.sms

protocol = 'https'
domain = 'api.solapi.com'
prefix = ''


def unique_id():
    return str(uuid.uuid1().hex)


def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


def get_signature(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def get_headers(api_key, api_secret):
    date = get_iso_datetime()
    salt = unique_id()
    combined_string = date + salt

    return {
        'Authorization': 'HMAC-SHA256 ApiKey=' + api_key + ', Date=' + date + ', salt=' + salt + ', signature=' +
                         get_signature(api_secret, combined_string),
        'Content-Type': 'application/json; charset=utf-8'
    }


def get_url(path):
    url = '%s://%s' % (protocol, domain)
    if prefix != '':
        url = url + prefix
    url = url + path
    return url


def send_many(parameter):
    api_key = account_env.sms.api_key
    api_secret = account_env.sms.api_secret
    parameter['agent'] = {
        'sdkVersion': 'python/4.2.0',
        'osPlatform': platform.platform() + " | " + platform.python_version()
    }

    return requests.post(get_url('/messages/v4/send-many'), headers=get_headers(api_key, api_secret), json=parameter)


def send_sms(message):
    data = {
        'messages': [
            {
                'to': account_env.sms.to_number,
                'from': account_env.sms.from_number,
                'text': message
            },
        ]
    }
    res = send_many(data)
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    send_sms("[KM WIFI] (긴급상황알림-가상상황) 성인 남성 1명이 쓰러졌습니다. 실험환경의 가상상황입니다.")
