// Replays demo-trace.json on the canvas. No external deps.
(async function () {
  const res = await fetch('demo-trace.json');
  const trace = await res.json();

  const canvas = document.getElementById('stage');
  const ctx = canvas.getContext('2d');
  const goalEl = document.getElementById('goal');
  const kindEl = document.getElementById('kind');
  const eventsEl = document.getElementById('events');
  const tabsEl = document.getElementById('scenario-buttons');
  const playBtn = document.getElementById('play');
  const resetBtn = document.getElementById('reset');

  const polygon = trace.robot.workspace_polygon;
  const obstacles = trace.robot.obstacles || [];
  const scenarios = trace.scenarios;

  // Workspace -> canvas mapping (workspace is -1.5 .. 1.5)
  const RANGE = 1.5;
  const SIZE = canvas.width;
  const toX = (x) => ((x + RANGE) / (2 * RANGE)) * SIZE;
  const toY = (y) => SIZE - ((y + RANGE) / (2 * RANGE)) * SIZE;

  let current = scenarios[0];
  let frame = 0;
  let timer = null;

  function renderTabs() {
    tabsEl.innerHTML = '';
    scenarios.forEach((s, i) => {
      const b = document.createElement('button');
      b.textContent = s.name;
      b.addEventListener('click', () => selectScenario(i));
      tabsEl.appendChild(b);
    });
    setActive(0);
  }
  function setActive(i) {
    [...tabsEl.children].forEach((c, j) => c.classList.toggle('active', i === j));
  }
  function selectScenario(i) {
    stop();
    current = scenarios[i];
    frame = 0;
    setActive(i);
    refreshSide();
    drawFrame();
  }

  function refreshSide() {
    goalEl.textContent = current.goal;
    kindEl.textContent = current.adversarial
      ? `Adversarial · expects block: ${current.expected_block_kind}`
      : 'Benign · should run clean';
    kindEl.classList.toggle('adversarial', current.adversarial);
    renderEvents([]);
  }

  function renderEvents(events) {
    eventsEl.innerHTML = '';
    events.forEach((e) => {
      const li = document.createElement('li');
      li.innerHTML = `t=${e.t.toFixed(1)}s · <code>${e.kind}</code> · ${e.reason}`;
      eventsEl.appendChild(li);
    });
  }

  function drawWorkspace() {
    ctx.save();
    ctx.fillStyle = '#0a1029';
    ctx.fillRect(0, 0, SIZE, SIZE);

    // Polygon
    ctx.strokeStyle = '#6b7280';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    polygon.forEach(([x, y], i) => {
      const px = toX(x), py = toY(y);
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    });
    ctx.closePath();
    ctx.stroke();
    ctx.setLineDash([]);

    // Obstacles
    obstacles.forEach(([x, y]) => {
      ctx.fillStyle = '#fca5a5';
      ctx.beginPath();
      ctx.arc(toX(x), toY(y), 8, 0, Math.PI * 2);
      ctx.fill();
    });

    // Origin crosshair
    ctx.strokeStyle = '#233055';
    ctx.beginPath();
    ctx.moveTo(toX(-RANGE), toY(0)); ctx.lineTo(toX(RANGE), toY(0));
    ctx.moveTo(toX(0), toY(-RANGE)); ctx.lineTo(toX(0), toY(RANGE));
    ctx.stroke();
    ctx.restore();
  }

  function drawFrame() {
    drawWorkspace();
    const samples = current.samples.slice(0, frame + 1);
    if (samples.length === 0) return;

    // Robot path so far
    ctx.strokeStyle = '#6ee7b7';
    ctx.lineWidth = 2;
    ctx.beginPath();
    samples.forEach((s, i) => {
      const x = toX(s.x), y = toY(s.y);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Intervention markers along the way
    samples.forEach((s) => {
      if (s.intervened) {
        ctx.fillStyle = '#fbbf24';
        ctx.beginPath();
        ctx.arc(toX(s.x), toY(s.y), 4, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Current robot pose
    const last = samples[samples.length - 1];
    ctx.fillStyle = '#6ee7b7';
    ctx.beginPath();
    ctx.arc(toX(last.x), toY(last.y), 7, 0, Math.PI * 2);
    ctx.fill();

    // Raw command arrow (what operator wanted)
    ctx.strokeStyle = '#93c5fd';
    ctx.lineWidth = 2;
    const SCALE = 50; // pixels per (m/s)
    const ang = last.theta;
    const x1 = toX(last.x), y1 = toY(last.y);
    const x2 = x1 + last.cmd_raw[0] * Math.cos(ang) * SCALE;
    const y2 = y1 - last.cmd_raw[0] * Math.sin(ang) * SCALE;
    ctx.beginPath();
    ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
    ctx.stroke();

    // Update events panel up to current frame
    const events = current.interventions.filter((e) => e.t <= last.t);
    renderEvents(events);
  }

  function tick() {
    frame++;
    if (frame >= current.samples.length) { stop(); return; }
    drawFrame();
  }
  function play() {
    if (timer) return;
    if (frame >= current.samples.length - 1) frame = 0;
    timer = setInterval(tick, 80);
  }
  function stop() { clearInterval(timer); timer = null; }
  function reset() { stop(); frame = 0; drawFrame(); }

  playBtn.addEventListener('click', play);
  resetBtn.addEventListener('click', reset);

  renderTabs();
  refreshSide();
  drawFrame();
})();
