#!/bin/bash

# 🔗 CUSTOM ALIASES FOR YOUR 2TB DRIVE
# Run this to add convenient shortcuts to your terminal

DRIVE="/Volumes/Seagate\ 2TB"
SHELL_CONFIG=""

# Detect shell and config file
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bash_profile"
fi

echo "🚀 Setting up custom aliases for your 2TB drive..."

# Add aliases to shell config
cat >> "$SHELL_CONFIG" << 'EOF'

# 🎯 2TB Drive Custom Aliases
alias drive='cd "/Volumes/Seagate 2TB"'
alias organize='"/Volumes/Seagate 2TB/Scripts/organize.sh"'
alias backup='"/Volumes/Seagate 2TB/Scripts/smart_backup.sh"'
alias drivereport='"/Volumes/Seagate 2TB/Scripts/organize.sh" report'

# Quick navigation
alias photos='cd "/Volumes/Seagate 2TB/Media/Photos"'
alias projects='cd "/Volumes/Seagate 2TB/Work"'
alias downloads='cd "/Volumes/Seagate 2TB/Temp/Downloads"'
alias creative='cd "/Volumes/Seagate 2TB/Creative"'

# Advanced Python Scripts
alias finddupes='python3 "/Volumes/Seagate 2TB/Scripts/duplicate_hunter.py"'
alias drivehealth='python3 "/Volumes/Seagate 2TB/Scripts/drive_guardian.py"'
alias projectmgr='python3 "/Volumes/Seagate 2TB/Scripts/project_manager.py"'
alias smartsearch='python3 "/Volumes/Seagate 2TB/Scripts/smart_search.py"'
alias cloudsync='python3 "/Volumes/Seagate 2TB/Scripts/cloud_sync.py"'
alias mediaprocess='"/Volumes/Seagate 2TB/Scripts/media_processor.sh"'

# Master Control Center
alias drivecontrol='python3 "/Volumes/Seagate 2TB/Scripts/master_control.py"'
alias drivedash='python3 "/Volumes/Seagate 2TB/Scripts/master_control.py" dashboard'
alias driveauto='python3 "/Volumes/Seagate 2TB/Scripts/master_control.py" auto'

# Utility functions
drivehelp() {
    echo "🎯 2TB Drive Commands:"
    echo "  drive       - Go to drive root"
    echo "  organize    - Run organization script"
    echo "  backup      - Run backup script"  
    echo "  drivereport - Show storage report"
    echo "  photos      - Go to photos folder"
    echo "  projects    - Go to work folder"
    echo "  downloads   - Go to downloads"
    echo "  creative    - Go to creative folder"
    echo ""
    echo "🚀 Advanced Commands:"
    echo "  finddupes   - Find duplicate files"
    echo "  drivehealth - Check drive health"
    echo "  projectmgr  - Manage projects"
    echo "  smartsearch - AI-powered file search"
    echo "  cloudsync   - Cloud synchronization"
    echo "  mediaprocess- Process media files"
    echo ""
    echo "🎛️ Master Control:"
    echo "  drivecontrol- Access master control"
    echo "  drivedash   - System dashboard"
    echo "  driveauto   - Run automation"
}

EOF

echo "✅ Aliases added to $SHELL_CONFIG"
echo "🔄 Run 'source $SHELL_CONFIG' or restart your terminal"
echo "💡 Type 'drivehelp' for command reference"