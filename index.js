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
});