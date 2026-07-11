#!/bin/zsh
# Install (or reinstall) the portfolio-agent reminder launchd agents.
# Usage: ./ops/install_reminders.sh          install + load
#        ./ops/install_reminders.sh remove   unload + delete

set -e
AGENTS_DIR="$HOME/Library/LaunchAgents"
SRC_DIR="$(cd "$(dirname "$0")/launchd" && pwd)"
LABELS=(com.portfolio-agent.earnings-reminder com.portfolio-agent.digest-reminder)

if [[ "$1" == "remove" ]]; then
    for label in $LABELS; do
        launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
        rm -f "$AGENTS_DIR/$label.plist"
        echo "removed $label"
    done
    exit 0
fi

mkdir -p "$AGENTS_DIR"
for label in $LABELS; do
    cp "$SRC_DIR/$label.plist" "$AGENTS_DIR/"
    launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$AGENTS_DIR/$label.plist"
    echo "installed + loaded $label"
done

echo
echo "Schedules (local machine time):"
echo "  earnings reminder : daily 09:00"
echo "  digest nudge      : Fridays 17:30"
echo "Log: ~/Library/Logs/portfolio-agent-reminders.log"
echo "Force a test run:  launchctl kickstart gui/\$(id -u)/com.portfolio-agent.earnings-reminder"
