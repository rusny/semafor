from websocket_server import IntersectionWebSocketServer
from restapi_server import fastApi
import sys
import signal
import threading
import uvicorn
from simulation import Simulation
import os

if __name__ == "__main__":
    terminateEvent = threading.Event()
    websocketServer = IntersectionWebSocketServer(host='0.0.0.0', port=9000)
    websocketServer.start()

    def signal_handler(sig, frame):
        print("SIGTERM received, shutting down...")
        websocketServer.stop()
        terminateEvent.set()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    
    # Nastavenie ciest k priečinkom
    current_dir = os.path.dirname(os.path.abspath(__file__))  # backend priečinok
    parent_dir = os.path.dirname(current_dir)  # koreňový priečinok
    frontend_dir = os.path.join(parent_dir, 'frontend')  # frontend priečinok
    
    # Nastavenie statických súborov
    fastApi.state.frontend_dir = frontend_dir
    fastApi.state.simulation = Simulation(websocketServer)
    
    # Spustenie FastAPI
    uvicorn.run(fastApi, host="0.0.0.0", port=8080)

    try:
        terminateEvent.wait()
    except KeyboardInterrupt:
        # Extra poistka pre prípad, že zachytávač signálov neuspeje
        print("Keyboard interrupt received, shutting down...")
        websocketServer.stop()

    print("Server has been shut down successfully")
    