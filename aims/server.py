from flask import Flask, render_template, url_for, request, jsonify
import json
import os
import logging
import ipdb

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path

        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from aims.ios import IOS
        from aims.android import adb
        from aims.android.android import Android
        from adbe import adb_enhanced as adbe
        import ipdb
        # Comment out debugging for normal operation
        # ipdb.set_trace(context=5) 
        # print('sflsd')
    else:
        from .ios.ios import IOS
        from .android import adb
        from .android.android import Android
        from adbe import adb_enhanced as adbe


template_dir = os.path.abspath('aims/templates')

app = Flask(__name__, template_folder=template_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize Android manager
android_manager = Android()


@app.route('/')
@app.route("/<data>")
def services(data=None):
    links = set()

    for rule in app.url_map.iter_rules():
        print(rule.endpoint)
        if rule.endpoint != 'static':
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


# Android Management Endpoints

@app.route('/androidlist')
def androidlist():
    """List connected Android devices with details."""
    try:
        devices = android_manager.get_device_details()
        return jsonify({
            "status": "success",
            "message": f"Found {len(devices)} Android devices",
            "data": devices
        })
    except Exception as e:
        app.logger.error(f"Failed to list Android devices: {str(e)}")
        return jsonify({"error": f"Failed to list devices: {str(e)}"}), 500


@app.route('/startandroidemu', methods=['POST'])
def startandroidemu():
    """Start Android emulator."""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data or 'avd_name' not in data:
            return jsonify({"error": "Missing required field: avd_name"}), 400
        
        avd_name = data['avd_name']
        result = android_manager.start_emulator(avd_name)
        
        if result['success']:
            return jsonify({
                "status": "success",
                "message": result['message'],
                "data": {"pid": result.get('pid')}
            })
        else:
            return jsonify({"error": result['message']}), 500
            
    except Exception as e:
        app.logger.error(f"Failed to start Android emulator: {str(e)}")
        return jsonify({"error": f"Failed to start emulator: {str(e)}"}), 500


@app.route('/killandroidemu', methods=['POST'])
def killandroidemu():
    """Kill Android emulator."""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data or 'serial' not in data:
            return jsonify({"error": "Missing required field: serial"}), 400
        
        serial = data['serial']
        result = android_manager.kill_emulator(serial)
        
        if result['success']:
            return jsonify({
                "status": "success",
                "message": result['message']
            })
        else:
            return jsonify({"error": result['message']}), 500
            
    except Exception as e:
        app.logger.error(f"Failed to kill Android emulator: {str(e)}")
        return jsonify({"error": f"Failed to kill emulator: {str(e)}"}), 500


@app.route('/getadblog')
def getadblog():
    """Get device logcat."""
    try:
        serial = request.args.get('serial')
        if not serial:
            return jsonify({"error": "Missing required parameter: serial"}), 400
        
        lines = request.args.get('lines', 100, type=int)
        log_lines = android_manager.get_device_log(serial, lines)
        
        return jsonify({
            "status": "success",
            "message": f"Retrieved {len(log_lines)} log lines",
            "data": {"logs": log_lines}
        })
        
    except Exception as e:
        app.logger.error(f"Failed to get ADB logs: {str(e)}")
        return jsonify({"error": f"Failed to get logs: {str(e)}"}), 500


@app.route('/listandroidapps')
def listandroidapps():
    """List apps on Android device."""
    try:
        serial = request.args.get('serial')
        if not serial:
            return jsonify({"error": "Missing required parameter: serial"}), 400
        
        apps = android_manager.list_apps(serial)
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(apps)} apps",
            "data": {"apps": apps}
        })
        
    except Exception as e:
        app.logger.error(f"Failed to list Android apps: {str(e)}")
        return jsonify({"error": f"Failed to list apps: {str(e)}"}), 500


@app.route('/createdroidemu', methods=['POST'])
def createdroidemu():
    """Create new Android emulator."""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data or 'name' not in data or 'system_image' not in data:
            return jsonify({"error": "Missing required fields: name, system_image"}), 400
        
        name = data['name']
        system_image = data['system_image']
        device_definition = data.get('device_definition', 'pixel')
        
        result = android_manager.create_emulator(name, system_image, device_definition)
        
        if result['success']:
            return jsonify({
                "status": "success",
                "message": result['message']
            })
        else:
            return jsonify({"error": result['message']}), 500
            
    except Exception as e:
        app.logger.error(f"Failed to create Android emulator: {str(e)}")
        return jsonify({"error": f"Failed to create emulator: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(port=8090, debug=True)
