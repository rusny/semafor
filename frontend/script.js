// Načítanie a vykreslenie križovatky
async function loadData() {
    try {
      const res = await fetch("http://localhost:8000/api/state");
      const data = await res.json();
      renderIntersection(data);
    } catch (err) {
      console.error("Chyba pri načítaní dát:", err);
    }
  }
  
  // Vygenerovanie novej konfigurácie križovatky
  async function configureIntersection() {
    const type = parseInt(document.getElementById("type").value);
    const cycle = parseInt(document.getElementById("cycle").value);
    const variant = document.getElementById("variant").value;
  
    const config = {
      type: type,
      cycle_duration: cycle,
      variant: variant,
      cycle_times: {
        left: { green: 10, yellow: 3, red: cycle - 13 },
        straight: { green: 20, yellow: 3, red: cycle - 23 },
        right: { green: 20, yellow: 3, red: cycle - 23 }
      }
    };
  
    try {
      const res = await fetch("http://localhost:8000/api/configure", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config)
      });
  
      if (res.ok) {
        alert("Križovatka bola vygenerovaná.");
        loadData();
      } else {
        const err = await res.text();
        alert("Chyba pri generovaní: " + err);
      }
    } catch (e) {
      console.error("Chyba pri odosielaní konfigurácie:", e);
      alert("Nepodarilo sa spojiť so serverom.");
    }
  }
  
  // Vizualizácia križovatky
  function renderIntersection(data) {
    const canvas = document.getElementById("intersection");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  
    data.semaphores.forEach((semaphore) => {
      const pos = getSemaphorePosition(semaphore.position, semaphore.linked_lane_id);
      const color = getColor(semaphore.state);
  
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 12, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.stroke();
    });
  }
  
  // Určí pozíciu semaforu podľa jeho pozície a pruhu
  function getSemaphorePosition(position, laneId = "") {
    const centerX = 250;
    const centerY = 250;
    const offset = 100;
  
    let dx = 0;
    let dy = 0;
    let offsetPos = 0;
  
    if (laneId.includes("1")) offsetPos = -20;
    else if (laneId.includes("2")) offsetPos = 0;
    else offsetPos = 20;
  
    switch (position) {
      case "north":
        dx = offsetPos;
        dy = -offset;
        break;
      case "south":
        dx = offsetPos;
        dy = offset;
        break;
      case "east":
        dx = offset;
        dy = offsetPos;
        break;
      case "west":
        dx = -offset;
        dy = offsetPos;
        break;
    }
  
    return { x: centerX + dx, y: centerY + dy };
  }
  
  // Farba semaforu podľa stavu
  function getColor(state) {
    switch (state) {
      case "green":
        return "green";
      case "yellow":
        return "yellow";
      case "red":
      default:
        return "red";
    }
  }
  
  window.onload = () => {
    loadData();
  };
  