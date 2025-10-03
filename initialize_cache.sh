#!/bin/bash

# Create cache directories if they don't exist
mkdir -p .buildcache/api
mkdir -p .buildcache/frontend

# Create empty index.json files
echo "{}" > .buildcache/api/index.json
echo "{}" > .buildcache/frontend/index.json

echo "Cache directories initialized with empty index.json files."
echo "You can now uncomment the cache_from directives in docker-compose.yml for future builds."