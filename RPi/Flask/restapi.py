import time
from os import getenv
from flask import Flask, jsonify, request, abort
import psutil

API_KEY = getenv("FLASK_API_KEY")

app = Flask(__name__)
@app.route('/system_usage', methods=['GET'])
def get_sys_usage():
    try:
        api_key = request.headers.get('x-api-key')
        if api_key != API_KEY:
            abort(401)
        # CPU and memory usage
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
            
        # Network statistics
        net_io = psutil.net_io_counters()
        kbytes_sent = round(net_io.bytes_sent / 1024, 2)
        kbytes_recv = round(net_io.bytes_recv / 1024, 2)
        
        # Disk usage
        disk_usage = psutil.disk_usage("/").percent
            
        # System uptime
        uptime = int((time.time() - psutil.boot_time()) // 60)
            
        # Comprehensive usage information
        usage_info = {
            "cpu_usage_%": cpu_usage,
            "mem_usage_%": mem_usage,
            "network": {
                "kbytes_sent": kbytes_sent,
                "kbytes_recv": kbytes_recv
            },
            "disk_usage_%": disk_usage,
            "uptime_min": uptime
        }
        return jsonify(usage_info)

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=False)