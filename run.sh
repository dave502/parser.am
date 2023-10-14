#!/bin/bash

# # Start the first process
python "./telegram/bot.py" &

# run database migration
#(cd db; alembic upgrade head &)

# # Start the second process
./cron/crawl.sh &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
