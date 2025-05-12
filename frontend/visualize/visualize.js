const directions = ['north', 'south', 'east', 'west'];

// 🟢 Inicializácia WebSocket klienta
const socket = new WebSocket("ws://localhost:9005"); 

socket.onopen = () => {
    console.log("✅ WebSocket connected");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.method === "signals_update") {
        updateVisualization(data.signals, data.time, data.cycle_length);
    }
};

socket.onerror = (error) => {
    console.error("❌ WebSocket error", error);
};

socket.onclose = () => {
    console.log("❎ WebSocket connection closed");
};

// 🔄 Aktualizácia vizualizácie na stránke
function updateVisualization(signals, time, cycleLength) {
    document.getElementById("time").innerText = `${time}s`;

    directions.forEach(dir => {
        const container = document.getElementById(dir);
        container.innerHTML = `<h2>${dir.toUpperCase()}</h2>`;
        const list = document.createElement("div");
        list.className = "direction-list";

        if (signals[dir]) {
            let orderedSignals = signals[dir];

            
            if (dir === 'north' || dir === 'east') {
                const priority = { right: 0, straight: 1, left: 2 };
                orderedSignals = [...signals[dir]].sort(
                    (a, b) => priority[a.direction] - priority[b.direction]
                );
            }

            orderedSignals.forEach(signal => {
                const div = document.createElement("div");
                div.classList.add("signal", signal.direction);
                if (!signal.active) {
                    div.classList.add("inactive");
                }
                div.innerText = signal.direction.toUpperCase();
                list.appendChild(div);
            });
        }

        container.appendChild(list);
    });
}
