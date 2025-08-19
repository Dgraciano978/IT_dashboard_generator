#!/bin/bash
# IT Dashboard Generator - Unix/Linux Cron Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting IT Dashboard Generator..."
echo "$(date)"

cd "$PROJECT_DIR"
mkdir -p logs

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> logs/scheduler.log
    echo "$1"
}

if [ -f "venv/bin/activate" ]; then
    log_message "Activating virtual environment..."
    source venv/bin/activate
fi

export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
log_message "Running dashboard generator..."
python3 main.py --config config/settings.json

if [ $? -eq 0 ]; then
    log_message "Dashboard generation completed successfully"
else
    log_message "ERROR: Dashboard generation failed with exit code $?"
    exit 1
fi

log_message "Finished at $(date)"
