#!/bin/bash
# Run the BDE entrypoint to configure hive-site.xml, then run schematool
source /entrypoint.sh echo 2>/dev/null || true
/opt/hive/bin/schematool -dbType postgres -initSchema
