const userId = {userId}; // Replace with actual user ID
const socket = new WebSocket(`ws://<span class="math-inline">\{window\.location\.host\}/ws/location/</span>{userId}/`);

socket.onmessage = function(event) {
    const data = JSON.parse(event.data)};