#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================================="
echo " Starting Civ 5 AI Advisor (Memory Cheats Enabled)"
echo " Administrator privileges are required to access game memory."
echo "=========================================================="

PYTHON_PATH=$(which python3)

# Check if python has the debugger entitlement
if ! codesign -d --entitlements - "$PYTHON_PATH" 2>&1 | grep -q "com.apple.security.cs.debugger"; then
    echo "Adding memory debugger entitlement to Python to allow Frida injection..."
    cat << 'EOF' > /tmp/ents.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.debugger</key>
    <true/>
</dict>
</plist>
EOF
    sudo codesign -s - -f --entitlements /tmp/ents.plist "$PYTHON_PATH"
fi

sudo "$PYTHON_PATH" app.py
