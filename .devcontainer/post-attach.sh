#!/usr/bin/env bash
# Post-attach command: Runs when a user attaches to an existing container
# This automatically starts the initialization when using "Use this template" + Codespaces/DevContainer

set -e

# Check if this is still a blueprint (not yet initialized)
if [ -f "initialize.sh" ] && grep -q "ha_integration_domain" custom_components/*/manifest.json 2>/dev/null; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════════╗"
    echo "║  🚀 Welcome to your new Home Assistant Integration!                     ║"
    echo "╚══════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "This appears to be a fresh copy of the blueprint."
    echo "Starting initialization process..."
    echo ""

    # Run initialization script
    ./initialize.sh
fi
