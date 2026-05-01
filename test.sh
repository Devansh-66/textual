#!/bin/bash
set -e
OUTPUT=""
MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output_path)
      OUTPUT="$2"
      shift 2
      ;;
    base|new)
      MODE="$1"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$OUTPUT" ]; then
  OUTPUT="results.xml"
fi

if [ "$MODE" = "base" ]; then
  pytest tests/test_geometry.py --junitxml="$OUTPUT"
else
  pytest tests/test_hexdump.py --junitxml="$OUTPUT"
fi
