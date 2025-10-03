# Docker Build Optimization Guide

This document explains the changes made to optimize Docker build times for the Coin Price Monitor application.

## Summary of Changes

1. Added `.dockerignore` files to reduce build context size
2. Implemented multi-stage builds for smaller, faster images
3. Optimized dependency installation
4. Improved layer caching
5. Enabled BuildKit for advanced caching and parallel builds
6. Added local build cache persistence

## Detailed Explanation

### 1. Added `.dockerignore` Files

**Files created:**
- `.dockerignore` (root directory)
- `frontend/.dockerignore`

**Impact:**
- Reduces the amount of data sent to the Docker daemon during builds
- Excludes unnecessary files like `.git`, virtual environments, and logs
- Significantly speeds up the initial build context transfer

### 2. Implemented Multi-Stage Builds

**Files modified:**
- `Dockerfile`
- `frontend/Dockerfile`

**Changes:**
- Split builds into separate stages: dependencies and final image
- Only necessary files are copied to the final image
- Reduced final image size by excluding build tools and intermediate files

**Impact:**
- Smaller final images (faster to push/pull)
- Better separation of build and runtime dependencies
- More efficient caching of build stages

### 3. Optimized Dependency Installation

**Changes:**
- Backend: Pre-built wheels for Python packages
- Frontend: Used `npm ci` instead of `npm install` for faster, more reliable installation
- Simplified package installation commands

**Impact:**
- Faster dependency installation
- More reliable builds with deterministic dependencies
- Better caching of dependency layers

### 4. Improved Layer Caching

**Changes:**
- Ordered Dockerfile commands from least to most likely to change
- Copied only necessary files at each stage
- Used specific COPY commands instead of copying entire directories

**Impact:**
- Better utilization of Docker's layer caching
- Fewer cache invalidations during builds
- Faster rebuilds when only application code changes

### 5. Enabled BuildKit

**File modified:**
- `docker-compose.yml`

**Changes:**
- Set `DOCKER_BUILDKIT: 1`
- Enabled inline caching with `BUILDKIT_INLINE_CACHE: 1`
- Used BuildKit-specific cache directives

**Impact:**
- Parallel processing of build stages
- More efficient caching mechanisms
- Better build output and progress reporting

### 6. Added Local Build Cache Persistence

**Changes:**
- Created `.buildcache` directory with subdirectories for each service
- Added `cache_from` and `cache_to` directives in docker-compose.yml
- Used named volume for PostgreSQL data

**Impact:**
- Persists cache between builds even after Docker prune operations
- Faster builds after initial setup
- Persistent database data between container restarts

## How to Use

To take advantage of these optimizations:

1. Make sure Docker BuildKit is enabled:
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. Build the application using Docker Compose:
   ```bash
   docker-compose build
   ```

3. For subsequent builds, the cache will be automatically used:
   ```bash
   docker-compose up --build
   ```

## Additional Optimization Tips

1. **Prune unused Docker objects regularly:**
   ```bash
   docker system prune -a
   ```

2. **Consider using Docker Desktop resource limits:**
   - Allocate appropriate CPU and memory resources
   - Enable disk image size limits

3. **For production builds:**
   - Consider using the `--no-cache` flag for clean builds
   - Use specific image tags instead of `latest`
   - Implement CI/CD pipeline caching

## Troubleshooting

If you encounter issues with BuildKit caching:

1. Clear the local build cache:
   ```bash
   rm -rf .buildcache
   mkdir -p .buildcache/api .buildcache/frontend
   ```

2. Disable BuildKit temporarily:
   ```bash
   DOCKER_BUILDKIT=0 docker-compose build
   ```

3. Check Docker daemon logs for any errors:
   ```bash
   docker system info
   ```