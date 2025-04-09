import threading
from simple_websocket_server import WebSocketServer, WebSocket


class SimpleClient(WebSocket):
    def handle(self):
        # Jednoduché spracovanie prichádzajúcich správ - nie je potrebné pre tento prípad
        pass

    def connected(self):
        # Pridanie klienta do zoznamu klientov servera
        self.server.clients.add(self)
        print(f"Client connected. Total clients: {len(self.server.clients)}")

    def handle_close(self):
        # Odstránenie klienta zo zoznamu klientov servera
        self.server.clients.remove(self)
        print(f"Client disconnected. Total clients: {len(self.server.clients)}")


class IntersectionWebSocketServer:
    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        """Spustenie WebSocket servera v samostatnom vlákne"""
        if self.running:
            print("Server is already running")
            return

        # Vytvorenie inštancie servera so zabudovaným sledovaním klientov
        class ServerWithClients(WebSocketServer):
            def __init__(self, host, port):
                super().__init__(host, port, SimpleClient)
                self.clients = set()

        self.server = ServerWithClients(self.host, self.port)

        # Spustenie servera v samostatnom vlákne
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.running = True
        print(f"WebSocket server started at ws://{self.host}:{self.port}")

    def stop(self):
        """Zastavenie WebSocket servera"""
        if not self.running:
            print("Server is not running")
            return

        if self.server:
            self.server.server_close()
            self.running = False
            if self.thread.is_alive():
                self.thread.join(timeout=5)
            print("WebSocket server stopped")

    def send_data(self, data):
        """Odoslanie dát všetkým pripojeným klientom"""
        if not self.running:
            print("Server is not running")
            return False

        # Získanie aktuálnej sady klientov
        clients = self.server.clients.copy()
        if not clients:
            print("No clients connected")
            return False

        # Odoslanie všetkým klientom
        success_count = 0
        for client in clients:
            try:
                client.send_message(data)
                success_count += 1
            except Exception as e:
                print(f"Error sending message: {e}")

        return success_count > 0