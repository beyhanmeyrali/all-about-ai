const transcriptContainer = document.getElementById('transcript-container');
const connectionDot = document.getElementById('connection-dot');
const connectionText = document.getElementById('connection-text');

// Device Elements
const acCard = document.getElementById('ac-card');
const acStatus = document.getElementById('ac-status');
const acTemp = document.getElementById('ac-temp');

const tvCard = document.getElementById('tv-card');
const tvStatus = document.getElementById('tv-status');

const doorCard = document.getElementById('door-card');
const doorStatus = document.getElementById('door-status');
const doorIcon = document.getElementById('door-icon');

// WebSocket Connection
let socket;

function connect() {
    socket = new WebSocket(`ws://${window.location.host}/ws`);

    socket.onopen = () => {
        connectionDot.classList.add('connected');
        connectionText.textContent = 'Connected';
        console.log('WebSocket Connected');
    };

    socket.onclose = () => {
        connectionDot.classList.remove('connected');
        connectionText.textContent = 'Disconnected - Reconnecting...';
        setTimeout(connect, 3000);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
}

function handleMessage(data) {
    if (data.type === 'speech') {
        addMessage(data.role, data.content);
    } else if (data.type === 'state_update') {
        updateState(data.state);
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const label = document.createElement('span');
    label.className = 'message-label';
    label.textContent = role === 'user' ? 'You' : 'Assistant';

    const text = document.createTextNode(content);

    messageDiv.appendChild(label);
    messageDiv.appendChild(text);

    transcriptContainer.appendChild(messageDiv);
    transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
}

function updateState(state) {
    // Update AC
    if (state.ac.power) {
        acCard.classList.add('active');
        acStatus.textContent = 'ON';
        acStatus.style.color = '#10b981';
        acTemp.style.display = 'block';
        acTemp.textContent = `${state.ac.temperature}°C`;
    } else {
        acCard.classList.remove('active');
        acStatus.textContent = 'OFF';
        acStatus.style.color = '#94a3b8';
        acTemp.style.display = 'none';
    }

    // Update TV
    if (state.tv.power) {
        tvCard.classList.add('active');
        tvStatus.textContent = 'ON';
        tvStatus.style.color = '#10b981';
    } else {
        tvCard.classList.remove('active');
        tvStatus.textContent = 'OFF';
        tvStatus.style.color = '#94a3b8';
    }

    // Update Door
    if (state.door.locked) {
        doorCard.classList.remove('unlocked');
        doorCard.classList.add('locked');
        doorStatus.textContent = 'LOCKED';
        doorStatus.style.color = '#ef4444';
        doorIcon.className = 'fas fa-lock device-icon';
    } else {
        doorCard.classList.remove('locked');
        doorCard.classList.add('unlocked');
        doorStatus.textContent = 'UNLOCKED';
        doorStatus.style.color = '#10b981';
        doorIcon.className = 'fas fa-lock-open device-icon';
    }
}

// Initial connection
connect();
