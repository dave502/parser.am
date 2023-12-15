#!/bin/bash

# Start the crawl process
./cron/crawl.sh &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
