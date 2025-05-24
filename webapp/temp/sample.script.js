// Ensure DOM is ready and Chart.js is available
document.addEventListener('DOMContentLoaded', () => {
    if (!window.Chart) {
        console.error('Chart.js not loaded. Please ensure the Chart.js CDN is included.');
        return;
    }

    // Sidebar toggle for mobile
    const toggleSidebar = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');
    if (toggleSidebar && sidebar) {
        toggleSidebar.addEventListener('click', () => {
            sidebar.classList.toggle('sidebar-hidden');
        });
    } else {
        console.error('Sidebar toggle elements not found: #toggleSidebar or #sidebar');
    }

    // Sidebar navigation
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    const sections = document.querySelectorAll('section');

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
            link.classList.remove('bg-gray-600');
            if (link.dataset.section === sectionId) {
                link.classList.add('bg-gray-600');
            }
        });
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

    // API base URL (adjust if Flask runs on a different host/port)
    const API_BASE_URL = 'http://localhost:5000';

    // Helper function to validate API data
    function validateData(data, section) {
        if (!data || typeof data !== 'object') {
            console.error(`Invalid data for ${section}:`, data);
            return false;
        }
        if (!data.line || !Array.isArray(data.line.timestamps) || !data.bar || !Array.isArray(data.bar.labels) || !Array.isArray(data.table)) {
            console.error(`Incomplete data structure for ${section}:`, data);
            return false;
        }
        return true;
    }

    // Function to fetch and update CPU data
    async function updateCpuData() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/cpu`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch CPU data`);
            const data = await response.json();
            if (!validateData(data, 'CPU')) return;

            if (chartInstances.cpuLineChart) {
                chartInstances.cpuLineChart.data.labels = data.line.timestamps;
                chartInstances.cpuLineChart.data.datasets[0].data = data.line.utilization;
                chartInstances.cpuLineChart.update();
            }
            if (chartInstances.cpuBarChart) {
                chartInstances.cpuBarChart.data.labels = data.bar.labels;
                chartInstances.cpuBarChart.data.datasets[0].data = data.bar.cpuTime;
                chartInstances.cpuBarChart.update();
            }

            const cpuTable = document.getElementById('cpuTable');
            if (cpuTable) {
                cpuTable.innerHTML = '';
                data.table.forEach(row => {
                    if (row.pid && row.name && row.cpuTime && row.memory && row.timestamp) {
                        const tr = document.createElement('tr');
                        tr.classList.add('table-row-hover');
                        tr.innerHTML = `
                            <td class="border px-4 py-2">${row.pid}</td>
                            <td class="border px-4 py-2">${row.name}</td>
                            <td class="border px-4 py-2">${row.cpuTime}</td>
                            <td class="border px-4 py-2">${row.memory}</td>
                            <td class="border px-4 py-2">${row.timestamp}</td>
                        `;
                        cpuTable.appendChild(tr);
                    } else {
                        console.warn('Incomplete CPU table row:', row);
                    }
                });
            } else {
                console.error('CPU table element not found: #cpuTable');
            }
        } catch (error) {
            console.error('Error updating CPU data:', error.message);
        }
    }

    // Function to fetch and update Alarms data
    async function updateAlarmsData() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/alarms`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch Alarms data`);
            const data = await response.json();
            if (!validateData(data, 'Alarms')) return;

            if (chartInstances.alarmsLineChart) {
                chartInstances.alarmsLineChart.data.labels = data.line.timestamps;
                chartInstances.alarmsLineChart.data.datasets[0].data = data.line.triggered;
                chartInstances.alarmsLineChart.update();
            }
            if (chartInstances.alarmsBarChart) {
                chartInstances.alarmsBarChart.data.labels = data.bar.labels;
                chartInstances.alarmsBarChart.data.datasets[0].data = data.bar.cpuPercent;
                chartInstances.alarmsBarChart.update();
            }

            const alarmsTable = document.getElementById('alarmsTable');
            if (alarmsTable) {
                alarmsTable.innerHTML = '';
                data.table.forEach(row => {
                    if (row.pid && row.name && row.cpuPercent && row.threshold && row.targetedAt) {
                        const tr = document.createElement('tr');
                        tr.classList.add('table-row-hover');
                        tr.innerHTML = `
                            <td class="border px-4 py-2">${row.pid}</td>
                            <td class="border px-4 py-2">${row.name}</td>
                            <td class="border px-4 py-2">${row.cpuPercent}</td>
                            <td class="border px-4 py-2">${row.threshold}</td>
                            <td class="border px-4 py-2">${row.targetedAt}</td>
                        `;
                        alarmsTable.appendChild(tr);
                    } else {
                        console.warn('Incomplete Alarms table row:', row);
                    }
                });
            } else {
                console.error('Alarms table element not found: #alarmsTable');
            }
        } catch (error) {
            console.error('Error updating Alarms data:', error.message);
        }
    }

    // Function to fetch and update User Activity data
    async function updateUserActivityData() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/user-activity`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch User Activity data`);
            const data = await response.json();
            if (!validateData(data, 'User Activity')) return;

            if (chartInstances.userActivityLineChart) {
                chartInstances.userActivityLineChart.data.labels = data.line.timestamps;
                chartInstances.userActivityLineChart.data.datasets[0].data = data.line.actions;
                chartInstances.userActivityLineChart.update();
            }
            if (chartInstances.userActivityBarChart) {
                chartInstances.userActivityBarChart.data.labels = data.bar.labels;
                chartInstances.userActivityBarChart.data.datasets[0].data = data.bar.counts;
                chartInstances.userActivityBarChart.update();
            }

            const userActivityTable = document.getElementById('userActivityTable');
            if (userActivityTable) {
                userActivityTable.innerHTML = '';
                data.table.forEach(row => {
                    if (row.action && row.pid && row.time) {
                        const tr = document.createElement('tr');
                        tr.classList.add('table-row-hover');
                        tr.innerHTML = `
                            <td class="border px-4 py-2">${row.action}</td>
                            <td class="border px-4 py-2">${row.pid}</td>
                            <td class="border px-4 py-2">${row.time}</td>
                        `;
                        userActivityTable.appendChild(tr);
                    } else {
                        console.warn('Incomplete User Activity table row:', row);
                    }
                });
            } else {
                console.error('User Activity table element not found: #userActivityTable');
            }
        } catch (error) {
            console.error('Error updating User Activity data:', error.message);
        }
    }

    // Function to fetch and update Process Manipulation data
    async function updateProcessesData() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/processes`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch Processes data`);
            const data = await response.json();
            if (!validateData(data, 'Processes')) return;

            if (chartInstances.processLineChart) {
                chartInstances.processLineChart.data.labels = data.line.timestamps;
                chartInstances.processLineChart.data.datasets[0].data = data.line.counts;
                chartInstances.processLineChart.update();
            }
            if (chartInstances.processBarChart) {
                chartInstances.processBarChart.data.labels = data.bar.labels;
                chartInstances.processBarChart.data.datasets[0].data = data.bar.counts;
                chartInstances.processBarChart.update();
            }

            const processesTable = document.getElementById('processesTable');
            if (processesTable) {
                processesTable.innerHTML = '';
                data.table.forEach(row => {
                    if (row.action && row.target && row.status && row.time) {
                        const tr = document.createElement('tr');
                        tr.classList.add('table-row-hover');
                        tr.innerHTML = `
                            <td class="border px-4 py-2">${row.action}</td>
                            <td class="border px-4 py-2">${row.target}</td>
                            <td class="border px-4 py-2 ${row.status === 'Success' ? 'text-[#a78bfa]' : row.status === 'Failed' ? 'text-[#f87171]' : 'text-[#f9a8d4]'}">${row.status}</td>
                            <td class="border px-4 py-2">${row.time}</td>
                        `;
                        processesTable.appendChild(tr);
                    } else {
                        console.warn('Incomplete Processes table row:', row);
                    }
                });
            } else {
                console.error('Processes table element not found: #processesTable');
            }
        } catch (error) {
            console.error('Error updating Processes data:', error.message);
        }
    }

    // Function to fetch and update Network data
    async function updateNetworkData() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/network`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch Network data`);
            const data = await response.json();
            if (!validateData(data, 'Network') || !Array.isArray(data.line.tcp) || !Array.isArray(data.line.udp)) return;

            if (chartInstances.networkLineChart) {
                chartInstances.networkLineChart.data.labels = data.line.timestamps;
                chartInstances.networkLineChart.data.datasets[0].data = data.line.tcp;
                chartInstances.networkLineChart.data.datasets[1].data = data.line.udp;
                chartInstances.networkLineChart.update();
            }
            if (chartInstances.networkBarChart) {
                chartInstances.networkBarChart.data.labels = data.bar.timestamps;
                chartInstances.networkBarChart.data.datasets[0].data = data.bar.packets;
                chartInstances.networkBarChart.update();
            }

            const networkTable = document.getElementById('networkTable');
            if (networkTable) {
                networkTable.innerHTML = '';
                data.table.forEach(row => {
                    if (row.timestamp && row.pid && row.uid && row.command && row.saddr && row.daddr && row.sport && row.dport && row.protocol && row.eventType) {
                        const tr = document.createElement('tr');
                        tr.classList.add('table-row-hover');
                        tr.innerHTML = `
                            <td class="border px-4 py-2">${row.timestamp}</td>
                            <td class="border px-4 py-2">${row.pid}</td>
                            <td class="border px-4 py-2">${row.uid}</td>
                            <td class="border px-4 py-2">${row.command}</td>
                            <td class="border px-4 py-2">${row.saddr}</td>
                            <td class="border px-4 py-2">${row.daddr}</td>
                            <td class="border px-4 py-2">${row.sport}</td>
                            <td class="border px-4 py-2">${row.dport}</td>
                            <td class="border px-4 py-2">${row.protocol}</td>
                            <td class="border px-4 py-2">${row.eventType}</td>
                        `;
                        networkTable.appendChild(tr);
                    } else {
                        console.warn('Incomplete Network table row:', row);
                    }
                });
            } else {
                console.error('Network table element not found: #networkTable');
            }
        } catch (error) {
            console.error('Error updating Network data:', error.message);
        }
    }

    // Initial data fetch
    Promise.all([
        updateCpuData(),
        updateAlarmsData(),
        updateUserActivityData(),
        updateProcessesData(),
        updateNetworkData()
    ]).catch(error => {
        console.error('Error during initial data fetch:', error.message);
    });

    // Real-time data updates every 60 seconds
    setInterval(() => {
        Promise.all([
            updateCpuData(),
            updateAlarmsData(),
            updateUserActivityData(),
            updateProcessesData(),
            updateNetworkData()
        ]).catch(error => {
            console.error('Error during periodic data update:', error.message);
        });
    }, 60000);
});