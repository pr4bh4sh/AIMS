from flask import Flask, render_template, url_for, request, jsonify
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path

        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from aims.ios import IOS
        from aims.android import Android, adb
        from adbe import adb_enhanced as adbe
    else:
        from .ios.ios import IOS
        from .android import Android, adb
        from adbe import adb_enhanced as adbe


template_dir = os.path.abspath('aims/templates')

app = Flask(__name__, template_folder=template_dir)

# Initialize managers
try:
    android_manager = Android()
    logger.info("Android manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Android manager: {e}")
    android_manager = None


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
        if not android_manager:
            return jsonify({"error": "Android manager not initialized"}), 500
            
        devices = android_manager.refresh_devices()
        device_details = []
        
        for serial in devices:
            details = android_manager.get_device_details(serial)
            device_details.append(details)
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(device_details)} devices",
            "data": device_details
        })
    except Exception as e:
        logger.error(f"Error in androidlist: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/startandroidemu', methods=['POST'])
def startandroidemu():
    """Start Android emulator."""
    try:
        if not android_manager:
            return jsonify({"error": "Android manager not initialized"}), 500
            
        data = request.get_json()
        if not data or 'avd_name' not in data:
            return jsonify({"error": "avd_name is required"}), 400
            
        result = android_manager.start_emulator(data['avd_name'])
        return jsonify({
            "status": "success",
            "message": f"Started emulator {data['avd_name']}",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error in startandroidemu: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/killandroidemu', methods=['POST'])
def killandroidemu():
    """Kill Android emulator."""
    try:
        if not android_manager:
            return jsonify({"error": "Android manager not initialized"}), 500
            
        data = request.get_json()
        if not data or 'serial' not in data:
            return jsonify({"error": "serial is required"}), 400
            
        result = android_manager.kill_emulator(data['serial'])
        return jsonify({
            "status": "success",
            "message": f"Killed emulator {data['serial']}",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error in killandroidemu: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/getadblog')
def getadblog():
    """Get device logcat."""
    try:
        if not android_manager:
            return jsonify({"error": "Android manager not initialized"}), 500
            
        serial = request.args.get('serial')
        if not serial:
            return jsonify({"error": "serial parameter is required"}), 400
            
        lines = request.args.get('lines', 100)
        try:
            lines = int(lines)
        except ValueError:
            lines = 100
            
        log_output = android_manager.get_device_log(serial, lines)
        return jsonify({
            "status": "success",
            "message": f"Retrieved {lines} lines from {serial}",
            "data": {
                "serial": serial,
                "lines": lines,
                "log": log_output
            }
        })
    except Exception as e:
        logger.error(f"Error in getadblog: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/listandroidapps')
def listandroidapps():
    """List apps on device."""
    try:
        if not android_manager:
            return jsonify({"error": "Android manager not initialized"}), 500
            
        serial = request.args.get('serial')
        if not serial:
            return jsonify({"error": "serial parameter is required"}), 400
            
        apps = android_manager.list_apps(serial)
        return jsonify({
            "status": "success",
            "message": f"Found {len(apps)} apps on {serial}",
            "data": {
                "serial": serial,
                "apps": apps
            }
        })
    except Exception as e:
        logger.error(f"Error in listandroidapps: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/createdroidemu', methods=['POST'])
def createdroidemu():
    """Create new emulator."""
    try:
        if not android_manager:
            return jsonify({"error": "Android manager not initialized"}), 500
            
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'system_image', 'device_definition']):
            return jsonify({
                "error": "name, system_image, and device_definition are required"
            }), 400
            
        result = android_manager.create_emulator(
            data['name'], 
            data['system_image'], 
            data['device_definition']
        )
        return jsonify({
            "status": "success",
            "message": f"Created emulator {data['name']}",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error in createdroidemu: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=8090, debug=True)
