from flask import Flask, render_template, url_for
import json
import os

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path

        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from aims.ios import IOS
    else:
        from .ios.ios import IOS

template_dir = os.path.abspath('aims/templates')

app = Flask(__name__, template_folder=template_dir)


@app.route('/')
@app.route("/<data>")
def all_links(data=None):
    links = []

    for rule in app.url_map.iter_rules():
        if rule.endpoint is not 'static':
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
        # if len(rule.defaults) >= len(rule.arguments):

    if data == "json":
        # return "json"
        return render_template('services.json.temp', links=links)

    return render_template("services.html", links=links)


@app.route('/ios-all')
def all_ios_config(html=None):
    # show the user profile for that user
    output = json.dumps(IOS().all, indent=4, sort_keys=True)
    if html:
        from bs4 import BeautifulSoup as bs
        ht = bs(output).prettify()
        return ht
    return output


@app.route('/ios-devices')
def devices():
    # show the user profile for that user
    return json.dumps(IOS().devices, indent=4, sort_keys=True)


@app.route('/ios-runtime')
def runtime():
    # show the user profile for that user
    return json.dumps(IOS().runtime, indent=4, sort_keys=True)


if __name__ == '__main__':
    app.run(port=8090, debug=True)
