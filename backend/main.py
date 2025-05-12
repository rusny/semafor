from websocket_server import IntersectionWebSocketServer
from restapi_server import semaphoreApp
import sys
import signal
import threading
import uvicorn
from simulation import Simulation
import os

if __name__ == "__main__":
    terminateEvent = threading.Event()
    # Upravený port pre WebSocket na 9005 podľa nginx konfigurácie
    websocketServer = IntersectionWebSocketServer(host='0.0.0.0', port=9005)
    websocketServer.start()

    def signal_handler(sig, frame):
        print("SIGTERM received, shutting down...")
        websocketServer.stop()
        terminateEvent.set()
        # Odstránené sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    
    # Nastavenie ciest k priečinkom
    current_dir = os.path.dirname(os.path.abspath(__file__))  # backend priečinok
    parent_dir = os.path.dirname(current_dir)  # koreňový priečinok
    frontend_dir = os.path.join(parent_dir, 'frontend')  # frontend priečinok
    
    # Nastavenie statických súborov
    semaphoreApp.state.frontend_dir = frontend_dir
    semaphoreApp.state.simulation = Simulation(websocketServer)
    
    # Spustenie FastAPI v samostatnom vlákne s portom 8085 podľa nginx konfigurácie
    fastapi_thread = threading.Thread(
        target=uvicorn.run,
        args=(semaphoreApp,),
        kwargs={"host": "0.0.0.0", "port": 8085}
    )
    fastapi_thread.daemon = True
    fastapi_thread.start()

    try:
        # Čakanie na ukončenie programu
        terminateEvent.wait()
        
        # Čakanie na dokončenie všetkých vlákien
        if fastapi_thread.is_alive():
            print("Čakanie na ukončenie FastAPI servera...")
            fastapi_thread.join(timeout=5)
            
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down...")
        websocketServer.stop()
        terminateEvent.set()

    print("Server has been shut down successfully")
