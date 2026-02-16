#!/bin/bash
echo "=== Freqtrade Starting ==="
freqtrade trade --config /freqtrade/config.json --strategy CombinedStrategy --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite 2>&1
EXIT_CODE=$?
echo "=== Freqtrade exited with code $EXIT_CODE ==="
echo "Keeping container alive..."
while true; do sleep 3600; done
