# Docker Build Cache Initialization

This document explains how to resolve the Docker build error related to missing cache files.

## The Issue

When running `docker-compose up --build`, you might encounter an error like this:

```
WARNING: local cache import at ./.buildcache/api not found due to err: could not read .buildcache/api/index.json: open .buildcache/api/index.json: no such file or directory
WARNING: local cache import at ./.buildcache/frontend not found due to err: could not read .buildcache/frontend/index.json: open .buildcache/frontend/index.json: no such file or directory
```

This error occurs because the Docker build is trying to use local cache directories that don't have the required index.json files.

## The Solution

We've implemented two solutions to address this issue:

1. **Temporary Fix**: We've commented out the `cache_from` directives in the docker-compose.yml file to prevent the build from trying to use non-existent cache files.

2. **Long-term Fix**: We've created an initialization script that creates the necessary cache directories and empty index.json files.

## How to Use

### First Build (Without Cache)

For the first build, simply run:

```bash
docker-compose up --build
```

This will build the containers without trying to use the cache.

### Initialize Cache for Future Builds

After the first successful build, you can initialize the cache directories for future builds:

```bash
./initialize_cache.sh
```

This script will:
- Create the .buildcache/api and .buildcache/frontend directories if they don't exist
- Create empty index.json files in these directories

### Enable Cache for Future Builds

Once the cache is initialized, you can uncomment the `cache_from` directives in the docker-compose.yml file:

```yaml
# Cache from previous builds
cache_from:
  - type=local,src=./.buildcache/api
```

And:

```yaml
# Cache from previous builds
cache_from:
  - type=local,src=./.buildcache/frontend
```

Then, future builds will be able to use the cache:

```bash
docker-compose up --build
```

## Troubleshooting

If you encounter issues with the cache:

1. Run the initialization script again:
   ```bash
   ./initialize_cache.sh
   ```

2. If problems persist, you can delete the cache directories and start fresh:
   ```bash
   rm -rf .buildcache
   mkdir -p .buildcache/api .buildcache/frontend
   ./initialize_cache.sh
   ```

3. As a last resort, you can keep the `cache_from` directives commented out in the docker-compose.yml file and build without cache.