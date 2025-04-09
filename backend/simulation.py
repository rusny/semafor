import threading
import time
import json
from websocket_server import IntersectionWebSocketServer
from schemas import Intersection


class Simulation:
    def __init__(self, websocketServer: IntersectionWebSocketServer):
        self.intersection = Intersection()
        self.current_time = 0
        self.simulation_thread = None
        self.stop_event = threading.Event()
        self.websocketServer = websocketServer
        self.simulation_speed = 1.0  # Sekundy reálneho času na 1 sekundu simulácie

    def update_intersection(self, intersection: Intersection):
        """Aktualizácia konfigurácie intersection"""
        self.intersection = intersection
        self.current_time = 0

    def simulate_step(self):
        """Vykonanie jedného kroku simulácie"""
        if self.intersection.cycle_length == 0:
            return  # Nie je čo simulovať
            
        # Získanie stavu semaforov pre aktuálny čas
        signals = self.intersection.get_signals_at_time(self.current_time)
        
        # Vytvorenie dátovej štruktúry pre websocket
        data = {
            "method": "signals_update",
            "time": self.current_time,
            "signals": signals,
            "cycle_length": self.intersection.cycle_length
        }
        
        # Odoslanie dát cez websocket
        self.websocketServer.send_data(json.dumps(data))
        
        # Inkrementácia času simulácie
        self.current_time = (self.current_time + 1) % self.intersection.cycle_length

    def simulation_loop(self):
        """Hlavná slučka simulácie"""
        while not self.stop_event.is_set():
            self.simulate_step()
            time.sleep(self.simulation_speed)

    def start_simulation(self):
        """Spustenie simulácie v samostatnom vlákne"""
        if self.simulation_thread is not None and self.simulation_thread.is_alive():
            # Simulácia už beží
            return
            
        self.stop_event.clear()
        self.simulation_thread = threading.Thread(target=self.simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        print("Simulation started")

    def stop_simulation(self):
        """Zastavenie simulácie"""
        if self.simulation_thread is not None:
            self.stop_event.set()
            self.simulation_thread.join(timeout=5)
            self.simulation_thread = None
            print("Simulation stopped")

    def set_simulation_speed(self, speed: float):
        """Nastavenie rýchlosti simulácie"""
        if speed > 0:
            self.simulation_speed = speed