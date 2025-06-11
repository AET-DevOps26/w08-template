#!/bin/bash

# Start the Grafana in the background
/run.sh &

# Wait until the Grafana service is up and running
until curl -s http://localhost:3001/api/health; do
  sleep 1
done

# WORK IN PROGRESS