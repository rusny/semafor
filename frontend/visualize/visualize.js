async function fetchSignals() {
    try {
        const response = await fetch('/get_signals');
        const data = await response.json();
        if (data && data.signals) {
            displaySignals(data.signals);
        }
    } catch (error) {
        console.error('Chyba pri načítaní signálov:', error);
    }
}

function displaySignals(signals) {
    const directions = ['north', 'south', 'east', 'west'];

    directions.forEach(dir => {
        const container = document.getElementById(dir);
        container.innerHTML = `<h2>${dir.toUpperCase()}</h2>`;

        if (signals[dir]) {
            signals[dir].forEach(signal => {
                const signalDiv = document.createElement('div');
                signalDiv.className = 'signal';
                signalDiv.innerText = `${signal.direction.toUpperCase()}`;
                signalDiv.style.color = signal.active ? 'green' : 'red';
                container.appendChild(signalDiv);
            });
        }
    });
}

setInterval(fetchSignals, 1000);

// Načítanie po načítaní stránky
window.onload = fetchSignals;
