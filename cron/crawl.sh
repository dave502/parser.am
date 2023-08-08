#!/bin/bash

if [ -z "$CRON_MODE" ]; then
   echo "CRON_MODE not set, assuming Development"
   CRON_MODE="Development"
fi

# Select the crontab file based on the environment
CRON_FILE="${ROOT_DIR}/cron/crontab.$CRON_MODE"

echo "Loading crontab file: $CRON_FILE"

# Remove commented-out lines
grep -v '^#' $CRON_FILE

# Load the crontab file
crontab $CRON_FILE

echo "Starting cron..."

# Start cron
cron -f