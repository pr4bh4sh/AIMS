from flask import Flask, render_template, url_for
import json
import os
import ipdb

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path

        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from aims.ios import IOS
        from aims.android import adb
        from adbe import adb_enhanced as adbe
        import ipdb
        ipdb.set_trace(context=5)
        print('sflsd')
    else:
        from .ios.ios import IOS
        from .android import adb
        from adbe import adb_enhanced as adbe


template_dir = os.path.abspath('aims/templates')

app = Flask(__name__, template_folder=template_dir)


@app.route('/')
@app.route("/<data>")
def services(data=None):
    links = set()

    for rule in app.url_map.iter_rules():
        print(rule.endpoint)
        if rule.endpoint is not 'static':
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.add(url)
        # if len(rule.defaults) >= len(rule.arguments):

    if data == "json":
        d_ = dict()
        d_['endpoints'] = [pn for pn in links]
        print(d_)
        # return "json"
        # return render_template('services.json.temp', links=links)
        return json.dumps(d_)
    return render_template("services.html", links=links)


@app.route('/ios-all')
@app.route('/ios-all/json')
def all_ios_config(html=None):
    # show the user profile for that user
    output = json.dumps(IOS().all, indent=4, sort_keys=True)
    if html:
        from bs4 import BeautifulSoup as bs
        ht = bs(output).prettify()
        return ht
    # print(f"{bs}")
    return output


@app.route('/ios-devices')
@app.route('/ios-devices/json')
def devices():
    # show the user profile for that user
    return json.dumps(IOS().devices, indent=4, sort_keys=True)


@app.route('/ios-runtime')
@app.route('/ios-runtime/json')
def runtime():
    # show the user profile for that user
    return json.dumps(IOS().runtime, indent=4, sort_keys=True)

@app.route('/android-devices')
def android_devices():
    # return json.dumps(adb.get_devices())
    return json.dumps(adbe.handle_list_devices())


if __name__ == '__main__':
    app.run(port=8090, debug=True)
