#!/bin/bash

# Get number of CPU cores
CORES=$(nproc)

echo "Starting $CORES high-CPU processes..."
for i in $(seq 1 $CORES); do
  yes > /dev/null &
done

echo "High CPU load started. Run 'pkill yes' to stop."
