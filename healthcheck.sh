#!/bin/sh

# Perform first healthcheck
curl -f http://localhost:8000
result1=$?

# Perform second healthcheck
curl -f http://localhost:8000/api/active_alarms/
result2=$?

# If either command failed, exit with an error status
if [ $result1 -ne 0 -o $result2 -ne 0 ]; then
  exit 1
fi

# Otherwise exit with a success status
exit 0

