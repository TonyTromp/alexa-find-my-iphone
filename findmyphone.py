import logging
import requests
from pyicloud import PyiCloudService
from flask import Flask, render_template
from flask_ask import Ask, statement

api = PyiCloudService('tony.tromp@gmail.com');

app = Flask(__name__)
ask = Ask(app, '/')
devices = api.devices;

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_inst():
  return 'HELLO and WELCOME';

@ask.intent('FindiDeviceIntend', convert={'device': 'LIST_OF_DEVICES'})
def FindiDeviceIntend(device):
    for i in range(0,len(devices.values())):
      if ( (devices[i].content['deviceClass'].lower()==device.lower()) and (devices[i].content['batteryLevel']>0)) :
        devices[i].play_sound();

    text = render_template('FindiDeviceIntend', device=device)
    return statement(text).simple_card('FindiDeviceIntend', text)

def gmapaddress_from_gps(str_lat,str_lng):
    str_ret = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=#LAT#,#LNG#&sensor=false';
    str_ret = str_ret.replace("#LAT#", str_lat);
    str_ret = str_ret.replace("#LNG#", str_lng);
    return str_ret

@ask.intent('LocateiDeviceIntend', convert={'device': 'LIST_OF_DEVICES'})
def LocateiDeviceIntend(device):
    for i in range(0,len(devices.values())):
      if ( (devices[i].content['deviceClass'].lower()==device.lower()) and (devices[i].content['location'])) :
        devices = api.devices;
        str_lat = repr(devices[i].content['location']['latitude']);
        str_lng = repr(devices[i].content['location']['longitude']);
        positioning = devices[i].content['location']['positionType'];

        try:
            r = requests.get(gmapaddress_from_gps(str_lat,str_lng) );
            res=r.json();
            location = res['results'][0]['formatted_address'];
            text = render_template('LocateiDeviceIntend', device=device, location=location);
            return statement(text).simple_card('LocateiDeviceIntend', text);
        except requests.exceptions.RequestException as e:
            None; # fall through

    text = render_template('UnableToLocateiDevice', device=device)
    return statement(text).simple_card('UnableToLocateiDevice', text);

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
