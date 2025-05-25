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

          fillTable("cpuUtilizationTable", data.cpuUtilization || [], ["timestamp", "pid", "comm", "cpu_time"], false);
          fillTable("cpuAlarmsTable", data.cpuAlarms || [], ["pid", "comm", "cpu", "threshold", "triggeredAt"], false);
          fillTable("networkPacketsTable", data.networkPackets || [], ["timestamp", "pid", "comm", "event_type", "saddr", "daddr", "dport", "protocol"], false);
          fillTable("privilegedEventsTable", data.privilegedEvents || [], ["time", "pid", "uid", "comm", "syscall", "filename", "args", "insight"], false);
          fillTable("userActivityTable", data.userActivity || [], ["timestamp", "pid", "uid", "comm", "suspicious"], false);
          fillTable("processEventsTable", data.processEvents || [], ["timestamp", "pid", "ppid", "comm", "activity", "reason", "action"], false);
          fillTable("cpuLineUsageTable", data.cpuLineUsage.lines || [], ["function", "location", "samples", "percent"], false);

          // Update total CPU time
          const totalCpuTime = document.getElementById('totalCpuTime');
          if (totalCpuTime) {
              totalCpuTime.textContent = data.cpuLineUsage.total_cpu_time ;
          }
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