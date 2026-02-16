#!/bin/bash
echo "=== Starting Freqtrade ==="
echo "Config:"
cat /freqtrade/config.json | head -5
echo "..."
echo "Strategy files:"
ls -la /freqtrade/user_data/strategies/
echo "=== Launching ==="
freqtrade trade --config /freqtrade/config.json --strategy CombinedStrategy --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite 2>&1 || {
    echo "=== FREQTRADE CRASHED ==="
    echo "Keeping container alive for log inspection..."
    tail -f /dev/null
}
