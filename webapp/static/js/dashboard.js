// document.addEventListener('DOMContentLoaded', () => {
//     const cpuTable = document.getElementById('cpu-table');
//     const alarmsTable = document.getElementById('alarms-table');
//     const networkTable = document.getElementById('network-table');
//     const userTable = document.getElementById('user-table');
//     const privTable = document.getElementById('priv-table');

//     const eventSource = new EventSource('/stream');

//     function connectWebSocket() {
//     const ws = new WebSocket('ws://localhost:6790');
//     ws.onopen = () => {
//         console.log('Connected to WebSocket server');
//         errorMessage.classList.add('hidden');
//     };
//     ws.onmessage = (event) => { /* existing onmessage code */ };
//     ws.onerror = () => {
//         console.error('WebSocket connection error');
//         errorMessage.classList.remove('hidden');
//         setTimeout(connectWebSocket, 6790); // Retry after 5 seconds
//     };
//     ws.onclose = () => {
//         console.error('WebSocket connection closed');
//         errorMessage.classList.remove('hidden');
//         setTimeout(connectWebSocket, 6790); // Retry after 5 seconds
//     };
//     return ws;
// }
// const ws = connectWebSocket();

//     eventSource.onmessage = (event) => {
//         const data = JSON.parse(event.data);

//         // Update CPU Utilization
//         cpuTable.innerHTML = '';
//         data.cpuUtilization.forEach(item => {
//             const row = document.createElement('tr');
//             row.innerHTML = `
//                 <td>${item.timestamp}</td>
//                 <td>${item.pid}</td>
//                 <td>${item.comm}</td>
//                 <td>${item.cpu_time}</td>
//             `;
//             cpuTable.appendChild(row);
//         });

//         // Update CPU Alarms
//         alarmsTable.innerHTML = '';
//         data.cpuAlarms.forEach(item => {
//             const row = document.createElement('tr');
//             row.innerHTML = `
//                 <td>${item.pid}</td>
//                 <td>${item.comm}</td>
//                 <td>${item.cpu}</td>
//                 <td>${item.threshold}</td>
//                 <td>${item.triggeredAt}</td>
//             `;
//             alarmsTable.appendChild(row);
//         });

//         // Update Network Packets
//         networkTable.innerHTML = '';
//         data.networkPackets.forEach(item => {
//             const row = document.createElement('tr');
//             row.innerHTML = `
//                 <td>${item.timestamp}</td>
//                 <td>${item.pid}</td>
//                 <td>${item.comm}</td>
//                 <td>${item.event_type}</td>
//                 <td>${item.saddr}</td>
//                 <td>${item.sport}</td>
//                 <td>${item.daddr}</td>
//                 <td>${item.dport}</td>
//                 <td>${item.protocol}</td>
//             `;
//             networkTable.appendChild(row);
//         });

//         // Update User Activity
//         userTable.innerHTML = '';
//         data.userActivity.forEach(item => {
//             const row = document.createElement('tr');
//             row.innerHTML = `
//                 <td>${item.timestamp}</td>
//                 <td>${item.pid}</td>
//                 <td>${item.uid}</td>
//                 <td>${item.comm}</td>
//                 <td>${item.args}</td>
//                 <td class="${item.suspicious ? 'suspicious' : ''}">${item.suspicious ? 'Yes' : 'No'}</td>
//             `;
//             userTable.appendChild(row);
//         });

//         // Update Privileged Events
//         privTable.innerHTML = '';
//         data.privilegedEvents.forEach(item => {
//             const row = document.createElement('tr');
//             row.innerHTML = `
//                 <td>${item.time}</td>
//                 <td>${item.pid}</td>
//                 <td>${item.uid}</td>
//                 <td>${item.comm}</td>
//                 <td>${item.syscall}</td>
//                 <td>${item.filename}</td>
//                 <td>${JSON.stringify(item.args)}</td>
//                 <td>${item.insight}</td>
//             `;
//             privTable.appendChild(row);
//         });
//     };

//     eventSource.onerror = () => {
//         console.error('SSE connection error');
//         eventSource.close();
//     };
// });

document.addEventListener('DOMContentLoaded', () => {
    const errorMessage = document.getElementById('error-message');

    function toggleMenu() {
        document.getElementById('sidebar').classList.toggle('active');
        document.getElementById('mainContent').classList.toggle('shift');
    }

    function showSection(id) {
        document.querySelectorAll('.table-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(id).classList.add('active');
    }

    function initializeWebSocket() {
        const socket = new WebSocket('ws://localhost:6790');

        socket.onopen = () => {
            console.log('WebSocket connected');
            errorMessage.classList.add('hidden');
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Received WebSocket data:', data);
                updateTables(data);
                renderCharts(data);
            } catch (e) {
                console.error('Error processing WebSocket data:', e);
                errorMessage.classList.remove('hidden');
            }
        };

        socket.onerror = () => {
            console.error('WebSocket connection error');
            errorMessage.classList.remove('hidden');
        };

        socket.onclose = () => {
            console.error('WebSocket connection closed');
            errorMessage.classList.remove('hidden');
        };

        // Expose toggleMenu and showSection globally for HTML onclick
        window.toggleMenu = toggleMenu;
        window.showSection = showSection;
    }

    function updateTables(data) {
        const fillTable = (id, rows, columns) => {
            const tbody = document.querySelector(`#${id} tbody`);
            tbody.innerHTML = ''; // Clear existing rows
            rows.forEach(row => {
                const tr = document.createElement('tr');
                columns.forEach(col => {
                    const td = document.createElement('td');
                    td.textContent = col === 'args' && Array.isArray(row[col]) ? JSON.stringify(row[col]) : row[col];
                    tr.appendChild(td);
                });
                tbody.insertBefore(tr, tbody.firstChild);
            });
        };

        fillTable("cpuUtilizationTable", data.cpuUtilization || [], ["timestamp", "pid", "comm", "cpu_time"]);
        fillTable("cpuAlarmsTable", data.cpuAlarms || [], ["pid", "comm", "cpu", "threshold", "triggeredAt"]);
        fillTable("networkPacketsTable", data.networkPackets || [], ["timestamp", "pid", "comm", "event_type", "saddr", "daddr", "dport", "protocol"]);
        fillTable("privilegedEventsTable", data.privilegedEvents || [], ["time", "pid", "uid", "comm", "syscall", "filename", "args", "insight"]);
        fillTable("userActivityTable", data.userActivity || [], ["timestamp", "pid", "uid", "comm", "args", "suspicious"]);
    }

    function renderCharts(data) {
        if (window.charts) window.charts.forEach(c => c.destroy());
        window.charts = [];

        const createChart = (id, labels, label, dataPoints, color) => {
            const ctx = document.getElementById(id).getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels.slice(0, 20),
                    datasets: [{
                        label: label,
                        data: dataPoints.slice(0, 20),
                        borderColor: color,
                        backgroundColor: color + '33',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'top' } },
                    scales: {
                        x: { title: { display: true, text: 'Timestamp' } },
                        y: { beginAtZero: true, title: { display: true, text: label } }
                    }
                }
            });
            window.charts.push(chart);
        };

        // CPU Utilization Chart
        const cpuLabels = data.cpuUtilization?.map(row => row.timestamp) || [];
        const cpuData = data.cpuUtilization?.map(row => row.cpu_time) || [];
        createChart("cpuUtilizationChart", cpuLabels, "CPU Time (s)", cpuData, "#007bff");

        // CPU Alarms Chart
        const alarmLabels = data.cpuAlarms?.map(row => row.triggeredAt) || [];
        const alarmData = data.cpuAlarms?.map(row => row.cpu) || [];
        createChart("cpuAlarmsChart", alarmLabels, "CPU Time (s)", alarmData, "#dc3545");

        // User Activity Chart
        if (data.userActivity && data.userActivity.length > 0) {
            const userLabels = data.userActivity.map(row => row.timestamp);
            const userData = data.userActivity.map(row => row.pid); // Using PID as a proxy for activity count
            createChart("userActivityChart", userLabels, "Process ID", userData, "#28a745");
        }
    }

    // Initialize WebSocket
    initializeWebSocket();
});