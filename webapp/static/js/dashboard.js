document.addEventListener('DOMContentLoaded', () => {
    if (!window.Chart) {
        console.error('Chart.js not loaded. Please ensure the Chart.js CDN is included.');
        return;
    }

    // Improved sidebar functionality
    const toggleSidebar = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (toggleSidebar && sidebar) {
        toggleSidebar.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('sidebar-visible');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 768 && 
                !sidebar.contains(e.target) && 
                !toggleSidebar.contains(e.target)) {
                sidebar.classList.remove('sidebar-visible');
            }
        });
    } else {
        console.error('Sidebar toggle elements not found: #toggleSidebar or #sidebar');
    }

    // Sidebar navigation
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    const sections = document.querySelectorAll('section');

    // Updated showSection function
    function showSection(sectionId) {
        if (!sectionId) {
            console.error('No sectionId provided');
            return;
        }
        sections.forEach(section => {
            section.classList.add('hidden-section');
            if (section.id === sectionId) {
                section.classList.remove('hidden-section');
            }
        });
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.section === sectionId) {
                link.classList.add('active');
            }
        });

        // Close sidebar on mobile after section change
        if (window.innerWidth < 768) {
            sidebar.classList.remove('sidebar-visible');
        }
    }

    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.dataset.section;
            if (sectionId) {
                showSection(sectionId);
            } else {
                console.error('Sidebar link missing data-section attribute:', link);
            }
        });
    });

    // Show CPU section by default
    const defaultSection = document.getElementById('cpu') ? 'cpu' : sections[0]?.id;
    if (defaultSection) {
        showSection(defaultSection);
    } else {
        console.warn('No sections found to display by default');
    }

    // Initialize charts with empty data
    const charts = [
        {
            id: 'cpuPieChart',
            variable: 'cpuLineChart',
            config: {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'CPU Utilization', data: [], borderColor: '#3b82f6', backgroundColor: '#3b82f6', fill: false, tension: 0.4 }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Percentage (%)', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Time', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: {
                        legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } },
                        title: { display: true, text: 'CPU Utilization Over Time', color: '#e0e7ff', font: { size: 16, weight: 'bold' } }
                    }
                }
            }
        },
        {
            id: 'cpuBarChart',
            variable: 'cpuBarChart',
            config: {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{ label: 'CPU Time (s)', data: [], backgroundColor: '#3b82f6', borderColor: '#3b82f6', borderWidth: 1 }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'CPU Time (s)', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Process', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: { legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } } }
                }
            }
        },
        {
            id: 'alarmsPieChart',
            variable: 'alarmsLineChart',
            config: {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Triggered CPU', data: [], borderColor: '#ff6f61', backgroundColor: '#ff6f61', fill: false, tension: 0.4 }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'CPU %', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Time', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: {
                        legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } },
                        title: { display: true, text: 'Triggered CPU Over Time', color: '#e0e7ff', font: { size: 16, weight: 'bold' } }
                    }
                }
            }
        },
        {
            id: 'alarmsBarChart',
            variable: 'alarmsBarChart',
            config: {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{ label: 'CPU %', data: [], backgroundColor: '#ff6f61', borderColor: '#ff6f61', borderWidth: 1 }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'CPU %', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Process', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: { legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } } }
                }
            }
        },
        {
            id: 'userActivityPieChart',
            variable: 'userActivityLineChart',
            config: {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'User Actions', data: [], borderColor: '#00b7eb', backgroundColor: '#00b7eb', fill: false, tension: 0.4 }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Count', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Time', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: {
                        legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } },
                        title: { display: true, text: 'User Actions Over Time', color: '#e0e7ff', font: { size: 16, weight: 'bold' } }
                    }
                }
            }
        },
        {
            id: 'userActivityBarChart',
            variable: 'userActivityBarChart',
            config: {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{ label: 'Actions', data: [], backgroundColor: '#00b7eb', borderColor: '#00b7eb', borderWidth: 1 }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Count', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Process ID', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: { legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } } }
                }
            }
        },
        {
            id: 'processPieChart',
            variable: 'processLineChart',
            config: {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Manipulation Count', data: [], borderColor: '#8b5cf6', backgroundColor: '#8b5cf6', fill: false, tension: 0.4 }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Count', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Time', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: {
                        legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } },
                        title: { display: true, text: 'Manipulation Count Over Time', color: '#e0e7ff', font: { size: 16, weight: 'bold' } }
                    }
                }
            }
        },
        {
            id: 'processBarChart',
            variable: 'processBarChart',
            config: {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{ label: 'Actions', data: [], backgroundColor: '#8b5cf6', borderColor: '#8b5cf6', borderWidth: 1 }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Count', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Process', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: { legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } } }
                }
            }
        },
        {
            id: 'networkPieChart',
            variable: 'networkLineChart',
            config: {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'TCP', data: [], borderColor: '#ff2e63', backgroundColor: '#ff2e63', fill: false, tension: 0.4 },
                        { label: 'UDP', data: [], borderColor: '#5853ff', backgroundColor: '#5853ff', fill: false, tension: 0.4 }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Packets', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Time', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: {
                        legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } },
                        title: { display: true, text: 'Packet Counts Over Time', color: '#e0e7ff', font: { size: 16, weight: 'bold' } }
                    }
                }
            }
        },
        {
            id: 'networkBarChart',
            variable: 'networkBarChart',
            config: {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{ label: 'Packets', data: [], backgroundColor: '#ff2e63', borderColor: '#ff2e63', borderWidth: 1 }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Packets', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } },
                        x: { title: { display: true, text: 'Time', color: '#e0e7ff' }, ticks: { color: '#e0e7ff' } }
                    },
                    plugins: { legend: { position: 'top', labels: { color: '#e0e7ff', font: { weight: 'bold' } } } }
                }
            }
        }
    ];

    // Initialize charts
    const chartInstances = {};
    charts.forEach(chart => {
        const canvas = document.getElementById(chart.id);
        if (canvas) {
            chartInstances[chart.variable] = new Chart(canvas.getContext('2d'), chart.config);
        } else {
            console.error(`Canvas element not found: #${chart.id}`);
        }
    });

    // Add connection status indicator
    const statusIndicator = document.createElement('div');
    statusIndicator.id = 'connection-status';
    statusIndicator.style.position = 'fixed';
    statusIndicator.style.top = '1rem';
    statusIndicator.style.right = '1rem';
    statusIndicator.style.padding = '0.5rem 1rem';
    statusIndicator.style.borderRadius = '0.375rem';
    statusIndicator.style.zIndex = '50';
    document.body.appendChild(statusIndicator);

    function updateConnectionStatus(status, message) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.textContent = message;
            indicator.style.backgroundColor = status === 'connected' ? '#059669' : '#DC2626';
            indicator.style.color = 'white';
        }
    }

    // Debug logging function
    function debugLog(type, message, data = null) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [${type}] ${message}`);
        if (data) {
            console.log('Data:', data);
        }
    }

    // WebSocket Connection with debug logging
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname || 'localhost';
    const wsPort = '6790';
    const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}`;
    
    debugLog('WebSocket', `Attempting to connect to ${wsUrl}`);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        debugLog('WebSocket', 'Connection established');
        updateConnectionStatus('connected', '🟢 Connected');
    };

    ws.onclose = () => {
        debugLog('WebSocket', 'Connection closed');
        updateConnectionStatus('disconnected', '🔴 Disconnected');
        // Try to reconnect every 5 seconds
        setTimeout(() => {
            debugLog('WebSocket', 'Attempting to reconnect...');
            window.location.reload();
        }, 5000);
    };

    ws.onerror = (error) => {
        debugLog('WebSocket', 'Connection error', error);
        updateConnectionStatus('error', '⚠️ Connection Error');
    };

    ws.onmessage = (event) => {
        try {
            debugLog('WebSocket', 'Message received');
            const data = JSON.parse(event.data);
            debugLog('Data', 'Parsed WebSocket message', data);

            if (!data) {
                throw new Error('No data received');
            }

            // CPU data update with validation
            if (Array.isArray(data.cpuUtilization)) {
                debugLog('Chart', 'Updating CPU chart');
                try {
                    // Get last 10 data points for better visualization
                    const recentData = data.cpuUtilization.slice(-10);
                    const timestamps = recentData.map(item => {
                        const time = item.timestamp.split(' ')[1]; // Extract time part
                        return time;
                    });
                    const values = recentData.map(item => parseFloat(item.cpu_time) || 0);
                    
                    if (chartInstances.cpuLineChart) {
                        chartInstances.cpuLineChart.data.labels = timestamps;
                        chartInstances.cpuLineChart.data.datasets[0].data = values;
                        chartInstances.cpuLineChart.update();
                        debugLog('Chart', 'CPU chart updated successfully');
                    }

                    // Update CPU Bar Chart with top 5 processes
                    if (chartInstances.cpuBarChart) {
                        const sortedData = [...recentData].sort((a, b) => b.cpu_time - a.cpu_time).slice(0, 5);
                        chartInstances.cpuBarChart.data.labels = sortedData.map(item => item.comm);
                        chartInstances.cpuBarChart.data.datasets[0].data = sortedData.map(item => item.cpu_time);
                        chartInstances.cpuBarChart.update();
                    }
                } catch (chartError) {
                    debugLog('Error', 'Failed to update CPU chart', chartError);
                }
            }

            // Update CPU alarms
            if (Array.isArray(data.cpuAlarms)) {
                debugLog('Chart', 'Updating CPU alarms chart');
                try {
                    // Get last 10 alarms for better visualization
                    const recentAlarms = data.cpuAlarms.slice(-10);
                    const timestamps = recentAlarms.map(alarm => alarm.triggeredAt.split(' ')[1]); // Extract time part
                    const values = recentAlarms.map(alarm => parseFloat(alarm.cpu) || 0);
                    
                    if (chartInstances.alarmsLineChart) {
                        chartInstances.alarmsLineChart.data.labels = timestamps;
                        chartInstances.alarmsLineChart.data.datasets[0].data = values;
                        chartInstances.alarmsLineChart.update();
                    }

                    // Update Alarms Bar Chart with top 5 processes
                    if (chartInstances.alarmsBarChart) {
                        const topAlarms = [...recentAlarms]
                            .sort((a, b) => b.cpu - a.cpu)
                            .slice(0, 5);
                        chartInstances.alarmsBarChart.data.labels = topAlarms.map(alarm => alarm.comm);
                        chartInstances.alarmsBarChart.data.datasets[0].data = topAlarms.map(alarm => alarm.cpu);
                        chartInstances.alarmsBarChart.update();
                    }
                } catch (chartError) {
                    debugLog('Error', 'Failed to update CPU alarms chart', chartError);
                }
            }

            // Update User Activity
            if (data.userActivity && chartInstances.userActivityLineChart) {
                const timestamps = data.userActivity.map(activity => activity.timestamp);
                const counts = data.userActivity.map(activity => activity.count);
                
                chartInstances.userActivityLineChart.data.labels = timestamps;
                chartInstances.userActivityLineChart.data.datasets[0].data = counts;
                chartInstances.userActivityLineChart.update();
            }

            // Update Network data
            if (Array.isArray(data.networkPackets)) {
                debugLog('Chart', 'Updating Network charts');
                try {
                    const timestamps = data.networkPackets.map(packet => packet.timestamp.split(' ')[1]);
                    const packetsByProtocol = data.networkPackets.reduce((acc, packet) => {
                        acc[packet.protocol] = (acc[packet.protocol] || 0) + 1;
                        return acc;
                    }, {});

                    if (chartInstances.networkLineChart) {
                        chartInstances.networkLineChart.data.labels = timestamps;
                        chartInstances.networkLineChart.data.datasets[0].data = data.networkPackets
                            .filter(p => p.protocol === 'TCP').map(() => packetsByProtocol['TCP'] || 0);
                        chartInstances.networkLineChart.data.datasets[1].data = data.networkPackets
                            .filter(p => p.protocol === 'UDP').map(() => packetsByProtocol['UDP'] || 0);
                        chartInstances.networkLineChart.update();
                    }

                    // Update Network table
                    const networkTable = document.getElementById('networkTable');
                    if (networkTable) {
                        networkTable.innerHTML = data.networkPackets.map(packet => `
                            <tr class="table-row-hover">
                                <td class="border px-4 py-2">${packet.timestamp}</td>
                                <td class="border px-4 py-2">${packet.pid}</td>
                                <td class="border px-4 py-2">${packet.comm}</td>
                                <td class="border px-4 py-2">${packet.saddr}</td>
                                <td class="border px-4 py-2">${packet.daddr}</td>
                                <td class="border px-4 py-2">${packet.sport}</td>
                                <td class="border px-4 py-2">${packet.dport}</td>
                                <td class="border px-4 py-2">${packet.protocol}</td>
                                <td class="border px-4 py-2">${packet.event_type}</td>
                            </tr>
                        `).join('');
                    }
                } catch (error) {
                    debugLog('Error', 'Failed to update Network data', error);
                }
            }

            // Update Privileged Events
            if (Array.isArray(data.privilegedEvents)) {
                debugLog('Chart', 'Updating Privileged Events');
                try {
                    const recentEvents = data.privilegedEvents.slice(-10);
                    
                    // Update Line Chart - Events over time
                    if (chartInstances.processLineChart) {
                        const timestamps = recentEvents.map(event => {
                            const time = new Date(event.time).toLocaleTimeString();
                            return time;
                        });

                        // Count cumulative events over time
                        const eventCounts = timestamps.map((_, index) => index + 1);

                        chartInstances.processLineChart.data.labels = timestamps;
                        chartInstances.processLineChart.data.datasets[0].data = eventCounts;
                        chartInstances.processLineChart.update();
                    }

                    // Update Bar Chart - Events by command type
                    if (chartInstances.processBarChart) {
                        const eventsByCommand = recentEvents.reduce((acc, event) => {
                            const key = `${event.comm} (${event.syscall})`;
                            acc[key] = (acc[key] || 0) + 1;
                            return acc;
                        }, {});

                        chartInstances.processBarChart.data.labels = Object.keys(eventsByCommand);
                        chartInstances.processBarChart.data.datasets[0].data = Object.values(eventsByCommand);
                        chartInstances.processBarChart.update();
                    }

                    // Update Process table with detailed event information
                    const processesTable = document.getElementById('processesTable');
                    if (processesTable) {
                        processesTable.innerHTML = recentEvents.map(event => {
                            const timestamp = new Date(event.time).toLocaleString();
                            const argsString = event.args ? event.args.join(', ') : 'N/A';
                            return `
                                <tr class="table-row-hover">
                                    <td class="border px-4 py-2">${event.syscall}
                                        <div class="text-xs text-gray-400">Args: ${argsString}</div>
                                    </td>
                                    <td class="border px-4 py-2">
                                        ${event.comm} (${event.pid})
                                        <div class="text-xs text-gray-400">UID: ${event.uid}</div>
                                    </td>
                                    <td class="border px-4 py-2 text-yellow-400">
                                        ${event.insight}
                                        <div class="text-xs text-gray-400">${event.filename}</div>
                                    </td>
                                    <td class="border px-4 py-2">${timestamp}</td>
                                </tr>
                            `;
                        }).join('');
                    }
                } catch (error) {
                    debugLog('Error', 'Failed to update Privileged Events', error);
                }
            }

            // Update Application Profiler
            if (data.total_cpu_time !== undefined && Array.isArray(data.lines)) {
                debugLog('Profiler', 'Updating profiler data');
                try {
                    // Update total CPU time
                    const totalCpuTimeElement = document.getElementById('totalCpuTime');
                    if (totalCpuTimeElement) {
                        totalCpuTimeElement.textContent = DataTransferItemList.total_cpu_time.toFixed(2);
                    }

                    // Update profiler table
                    const profilerTable = document.getElementById('profilerTable');
                    if (profilerTable) {
                        profilerTable.innerHTML = data.lines.map(line => `
                            <tr class="table-row-hover">
                                <td class="border px-4 py-2 font-mono text-sm">${line.function}</td>
                                <td class="border px-4 py-2 font-mono text-sm">${line.location}</td>
                                <td class="border px-4 py-2 text-center">${line.samples}</td>
                                <td class="border px-4 py-2 text-right">${line.percent.toFixed(2)}%</td>
                                <td class="border px-4 py-2">
                                    <div class="w-full bg-gray-700 rounded-full h-2.5">
                                        <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${line.percent}%"></div>
                                    </div>
                                </td>
                            </tr>
                        `).join('');
                    }
                } catch (error) {
                    debugLog('Error', 'Failed to update profiler data', error);
                }
            }

            // Update tables
            updateTables(data);

        } catch (error) {
            debugLog('Error', 'Failed to process WebSocket message', error);
        }
    };

    // Debug function to manually test WebSocket
    window.testWebSocket = () => {
        debugLog('Test', 'Sending test message');
        try {
            ws.send(JSON.stringify({ type: 'test', message: 'Test message' }));
        } catch (error) {
            debugLog('Error', 'Failed to send test message', error);
        }
    };

    function updateTables(data) {
        // Update CPU table
        if (Array.isArray(data.cpuUtilization)) {
            const cpuTable = document.getElementById('cpuTable');
            if (cpuTable) {
                // Get top 5 processes by CPU time
                const topProcesses = [...data.cpuUtilization]
                    .sort((a, b) => b.cpu_time - a.cpu_time)
                    .slice(0, 5);

                cpuTable.innerHTML = topProcesses.map(entry => {
                    const cpuTime = parseFloat(entry.cpu_time);
                    return `
                        <tr class="table-row-hover">
                            <td class="border px-4 py-2">${entry.pid || 'N/A'}</td>
                            <td class="border px-4 py-2">${entry.comm || 'N/A'}</td>
                            <td class="border px-4 py-2">${!isNaN(cpuTime) ? cpuTime.toFixed(2) : 'N/A'}</td>
                            <td class="border px-4 py-2">${entry.timestamp || 'N/A'}</td>
                        </tr>
                    `;
                }).join('');
            }
        }

        // Update Alarms table
        if (Array.isArray(data.cpuAlarms)) {
            const alarmsTable = document.getElementById('alarmsTable');
            if (alarmsTable) {
                // Get last 5 alarms for the table
                const recentAlarms = data.cpuAlarms.slice(-5);
                alarmsTable.innerHTML = recentAlarms.map(alarm => {
                    const cpuValue = parseFloat(alarm.cpu);
                    return `
                        <tr class="table-row-hover">
                            <td class="border px-4 py-2">${alarm.pid || 'N/A'}</td>
                            <td class="border px-4 py-2">${alarm.comm || 'N/A'}</td>
                            <td class="border px-4 py-2">${!isNaN(cpuValue) ? cpuValue.toFixed(2) : 'N/A'}%</td>
                            <td class="border px-4 py-2">${alarm.threshold || 'N/A'}%</td>
                            <td class="border px-4 py-2">${alarm.triggeredAt || 'N/A'}</td>
                        </tr>
                    `;
                }).join('');
            }
        }
    }
});