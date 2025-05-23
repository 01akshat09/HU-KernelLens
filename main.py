# from gevent import monkey
# monkey.patch_all()
# from gevent.pywsgi import WSGIServer
# from webapp.app import create_app
# from src.cpu_monitor.cpu_monitor import CPUMonitor
# from src.network_monitor.network_monitor import NetworkMonitor
# from src.user_monitor.user_monitor import UserMonitor
# from src.priv_monitor.priv_monitor import PrivMonitor
# import asyncio

# async def main():
#     """
#     Initialize monitoring components and start the Flask server.
#     """
#     print("🔁 Initializing monitoring system...")
#     cpu_monitor = CPUMonitor()
#     network_monitor = NetworkMonitor()
#     user_monitor = UserMonitor()
#     priv_monitor = PrivMonitor()

#     app = create_app(cpu_monitor, network_monitor, user_monitor, priv_monitor)
#     print("🔁 Flask server starting on http://localhost:5000")
#     http_server = WSGIServer(('localhost', 5000), app)
#     http_server.serve_forever()

# if __name__ == "__main__":
#     asyncio.run(main())



from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer
import asyncio
from webapp.app import create_app
from src.websocket.server import start_websocket_server
from src.cpu_monitor.cpu_monitor import init_cpu_monitor
from src.network_monitor.network_monitor import init_network_monitor
from src.user_monitor.user_monitor import init_user_monitor
from src.priv_monitor.priv_monitor import init_priv_monitor

async def main():
    """
    Initialize monitoring components, start the Flask server, and WebSocket server.
    """
    print("🔁 Initializing monitoring system...")
    cpu_monitor = init_cpu_monitor()
    network_monitor = init_network_monitor()
    user_monitor = init_user_monitor()
    priv_monitor = init_priv_monitor()

    # Start Flask server in a separate greenlet
    app = create_app()  # No monitor arguments needed
    print("🔁 Flask server starting on http://localhost:5000")
    http_server = WSGIServer(('localhost', 5000), app)
    http_server.start()

    # Start WebSocket server
    print("🔁 Starting WebSocket server...")
    await start_websocket_server()

if __name__ == "__main__":
    asyncio.run(main())