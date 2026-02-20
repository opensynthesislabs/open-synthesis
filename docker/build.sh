#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE="${1:-ghcr.io/opensynthesislabs/open-synthesis-handler:latest}"

echo "Building $IMAGE"

# Stage files into docker build context
cp "$REPO_ROOT/src/open_synthesis/handler.py" "$SCRIPT_DIR/handler.py"
cp -r "$REPO_ROOT/prompts" "$SCRIPT_DIR/prompts"

# Build
docker build -t "$IMAGE" "$SCRIPT_DIR"

# Clean staged files
rm -f "$SCRIPT_DIR/handler.py"
rm -rf "$SCRIPT_DIR/prompts"

echo "Built: $IMAGE"
echo "Push with: docker push $IMAGE"
