async function submitConfiguration() {
    const branches = ["north", "south", "east", "west"];
    const directions = ["left", "straight", "right"];

    const phases = {};

    branches.forEach(branch => {
        const branchData = {};
        directions.forEach(dir => {
            const startInput = document.getElementById(`${branch}_${dir}_start`);
            const endInput = document.getElementById(`${branch}_${dir}_end`);

            const start = parseInt(startInput.value) || 0;
            const end = parseInt(endInput.value) || 0;

            branchData[dir] = { start, end };
        });
        phases[branch] = branchData;
    });

    const payload = { phases };

    try {
        const response = await fetch('/set_phases', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Konfigurácia úspešne odoslaná!');
        } else {
            alert(`❌ Chyba: ${result.message}`);
        }
    } catch (error) {
        alert(`❌ Chyba pri odosielaní: ${error}`);
    }
}
