document.addEventListener('DOMContentLoaded', () => {
    async function fetchOrders() {
        try {
            const response = await fetch('http://127.0.0.1:5000/orders');
            const orders = await response.json();
            const tableBody = document.getElementById('orders-table-body');
            tableBody.innerHTML = ''; // Clear existing rows

            // Append orders to the table
            orders.forEach(order => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${order.customer}</td>
                    <td>${order.order}</td>
                    <td>${order.dietary_restrictions}</td>
                `;
                tableBody.appendChild(row);
            });
        } catch (error) {
            console.error('Error fetching orders:', error);
        }
    }

    // Fetch orders on page load
    fetchOrders();

    // New real-time listening functionality
    const socket = io();
    const startListeningBtn = document.getElementById('startListeningBtn');
    const stopListeningBtn = document.getElementById('stopListeningBtn');
    const realtimeTextDiv = document.getElementById('realtimeText');
    const statusDiv = document.createElement('div');
    document.body.appendChild(statusDiv);

    startListeningBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/start_listening', { method: 'POST' });
            const result = await response.json();
            console.log(result.message);
            startListeningBtn.disabled = true;
            stopListeningBtn.disabled = false;
        } catch (error) {
            console.error('Error starting listening:', error);
        }
    });

    stopListeningBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/stop_listening', { method: 'POST' });
            const result = await response.json();
            console.log(result.message);
            startListeningBtn.disabled = false;
            stopListeningBtn.disabled = true;
        } catch (error) {
            console.error('Error stopping listening:', error);
        }
    });

    socket.on('realtime_text', (data) => {
        realtimeTextDiv.textContent += data.text;
    });

    // Initially disable the stop button
    stopListeningBtn.disabled = true;
});
