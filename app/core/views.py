
from flask import Blueprint, current_app, jsonify
from werkzeug.local import LocalProxy
import psutil
import os
from authentication import require_appkey

core = Blueprint('core', __name__)
logger = LocalProxy(lambda: current_app.logger)


@core.before_request
def before_request_func():
    current_app.logger.name = 'core'



@core.route('/system_information', methods=['GET'])
# @require_appkey
def system_information():
    virtual_memory = psutil.virtual_memory()
    net_io = psutil.net_io_counters()
    uptime_hours = 0
    with open("/proc/uptime", "r") as f:
        uptime = f.read().split(" ")[0].strip()
        uptime = int(float(uptime))
        uptime_hours = uptime // 3600

    data = {
        'os': {
            'uptime': uptime_hours
        },
        'memory': {
            'total': bytes_to_GB(virtual_memory.total),
            'available': bytes_to_GB(virtual_memory.available),
            'used': bytes_to_GB(virtual_memory.used),
            'percentage': virtual_memory.percent,
        },
        'cpu': {
            'usage': psutil.cpu_percent()
        },
        'network': {
            'sent': bytes_to_GB(net_io.bytes_sent),
            'received': bytes_to_GB(net_io.bytes_recv)
        }
        
    }
    return jsonify(data)

@core.route('/ikev_users', methods=['GET'])
# @require_appkey
def ikev_users():
    try:
        stream = os.popen('/usr/sbin/strongswan leases | head -n 1')
        res = stream.read()
        arr = res.split(",")[1:]
        data = {
            'total':  int(arr[0][arr[0].find("/")-1]),
            'online': int(arr[1].strip()[:1])
        }
        return jsonify(data)
    except:
        stream = os.popen('/usr/sbin/strongswan leases | head -n 1')
        res = stream.read()
        return res


def bytes_to_GB(bytes):
    gb = bytes/(1024*1024*1024)
    gb = round(gb, 2)
    return gb