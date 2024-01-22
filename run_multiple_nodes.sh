#!/bin/bash

# Number of instances you want to run
num_instances=5

# Start instances on ports 5000 to 5004
for ((i=0; i<num_instances; i++)); do
    port=$((5000 + i))
    export PORT=$port
    gnome-terminal -- python3 BlockChain/dev/app.py &
    sleep 1  # Add a small delay to ensure each instance starts
done

echo "$num_instances Flask instances are running on ports 5000 to $((5000 + num_instances - 1))."

