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
                  console.log('cpuLineUsage:', data.cpuLineUsage); // Added
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
            //   tbody.innerHTML = ''; // Clear existing rows
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

          fillTable("cpuUtilizationTable", data.cpuUtilization || [], ["timestamp", "pid", "comm", "cpu_time"], false);
          fillTable("cpuAlarmsTable", data.cpuAlarms || [], ["pid", "comm", "cpu", "threshold", "triggeredAt"], false);
          fillTable("networkPacketsTable", data.networkPackets || [], ["timestamp", "pid", "comm", "event_type", "saddr", "daddr", "dport", "protocol"], false);
          fillTable("privilegedEventsTable", data.privilegedEvents || [], ["time", "pid", "uid", "comm", "syscall", "filename", "args", "insight"], false);
          fillTable("userActivityTable", data.userActivity || [], ["timestamp", "pid", "uid", "comm", "suspicious"], false);
          fillTable("processEventsTable", data.processEvents || [], ["timestamp", "pid", "ppid", "comm", "activity", "reason", "action"], false);
         
        const cpuLineUsageRows = (data.cpuLineUsage?.lines || [])
            .filter(row => row.function !== '??' && row.function !== '??:0')
            .map(row => ({
                ...row,
                timestamp: data.cpuLineUsage?.timestamp || '',
                total_cpu_time: data.cpuLineUsage?.total_cpu_time 
            }));
            // fillTable("cpuLineUsageTable", cpuLineUsageRows, ["timestamp", "total_cpu_time","function", "location", "samples", "percent"]);

             let lastTimestamp = null;
            let lastTotalCpuTime = null;
            const tbody = document.querySelector(`#cpuLineUsageTable tbody`);
            cpuLineUsageRows.forEach((row, index) => {
                const tr = document.createElement('tr');
                
                // Timestamp cell
                const timestampTd = document.createElement('td');
                if (index === 0 || row.timestamp !== lastTimestamp) {
                    timestampTd.textContent = row.timestamp;
                    lastTimestamp = row.timestamp;
                } else {
                    timestampTd.textContent = ''; // Leave blank if same as previous
                }
                tr.appendChild(timestampTd);

                // Total CPU Time cell
                const totalCpuTd = document.createElement('td');
                if (index === 0 || row.total_cpu_time !== lastTotalCpuTime) {
                    totalCpuTd.textContent = row.total_cpu_time;
                    lastTotalCpuTime = row.total_cpu_time;
                    
                } else {
                    totalCpuTd.textContent = ''; // Leave blank if same as previous
                }
                tr.appendChild(totalCpuTd);

                // Function, Location, Samples, Percent cells
                ['function', 'location', 'samples', 'percent'].forEach(col => {
                    const td = document.createElement('td');
                    td.textContent = row[col];
                    tr.appendChild(td);
                });
                
                tbody.insertBefore(tr, tbody.firstChild);
            });
        }


  function renderCharts(data) {
          if (window.charts) window.charts.forEach(c => c.destroy());
          window.charts = [];

          const createChart = (id, labels, datasets, yAxisLabel) => {
              const ctx = document.getElementById(id).getContext('2d');
              const chart = new Chart(ctx, {
                  type: 'line',
                  data: {
                      labels: labels.slice(0, 20),
                      datasets: datasets
                  },
                  options: {
                      responsive: true,
                      plugins: {
                          legend: {
                              position: 'top',
                              labels: {
                                  color: '#ffffff',
                                  font: { size: 12 }
                              }
                          }
                      },
                      scales: {
                          x: {
                              title: {
                                  display: true,
                                  text: 'Time',
                                  color: '#b0b0b0',
                                  font: { size: 12 }
                              },
                              ticks: { color: '#b0b0b0', font: { size: 10 } }
                          },
                          y: {
                              beginAtZero: true,
                              title: {
                                  display: true,
                                  text: yAxisLabel,
                                  color: '#b0b0b0',
                                  font: { size: 12 }
                              },
                              ticks: { color: '#b0b0b0', font: { size: 10 } }
                          }
                      }
                  }
              });
              window.charts.push(chart);
          };

          // CPU Utilization Chart
          const cpuLabels = data.cpuUtilization?.map(row => row.timestamp) || [];
          const cpuData = data.cpuUtilization?.map(row => row.cpu_time) || [];
          createChart("cpuUtilizationChart", cpuLabels, [{
              label: 'CPU UTILIZATION',
              data: cpuData,
              borderColor: '#3b82f6',
              backgroundColor: 'transparent',
              fill: false,
              tension: 0.4,
              borderWidth: 2,
              pointRadius: 0
          }], "CPU %");

          // CPU Alarms Chart
          const alarmLabels = data.cpuAlarms?.map(row => row.triggeredAt) || [];
          const alarmData = data.cpuAlarms?.map(row => row.cpu) || [];
          createChart("cpuAlarmsChart", alarmLabels, [{
              label: 'TRIGGERED CPU',
              data: alarmData,
              borderColor: '#dc3545',
              backgroundColor: 'transparent',
              fill: false,
              tension: 0,
              borderWidth: 2,
              pointRadius: 0
          }], "CPU %");

          // Network Packets Chart (Only TCP)
          const packetLabels = data.networkPackets?.map(row => row.timestamp) || [];
          const tcpData = data.networkPackets?.map(row => row.protocol === 'TCP' ? 6 : 0) || [];
          createChart("networkPacketsChart", packetLabels, [
              {
                  label: 'TCP',
                  data: tcpData,
                  borderColor: '#dc3545',
                  backgroundColor: 'transparent',
                  fill: false,
                  tension: 0,
                  borderWidth: 2,
                  pointRadius: 0
              }
          ], "Packets");

          // User Activity Chart (Always render, even if no data)
          const userLabels = data.userActivity?.map(row => row.timestamp) || [];
          const userData = data.userActivity?.map(row => row.pid) || [];
          createChart("userActivityChart", userLabels, [{
              label: 'Process ID',
              data: userData,
              borderColor: '#28a745',
              backgroundColor: 'transparent',
              fill: false,
              tension: 0.4,
              borderWidth: 2,
              pointRadius: 0
          }], "Process ID");
      }
      // Initialize WebSocket
      initializeWebSocket();
  });