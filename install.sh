#!/bin/bash

# 🎛️ MASTER CONTROL CENTER INSTALLER
# Ultimate External Drive Management System

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Installation variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DRIVE=""
USER_HOME="$HOME"

# Function to print banner
print_banner() {
    echo -e "${PURPLE}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                🎛️ MASTER CONTROL CENTER                      ║"
    echo "║              Ultimate Drive Management System                ║"
    echo "║                     Installer v1.0                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to print colored messages
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}${BOLD}🚀 $1${NC}"
}

# Function to check system requirements
check_requirements() {
    log_step "Checking system requirements..."
    
    # Check macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This installer is designed for macOS only"
        exit 1
    fi
    
    # Check Python 3
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python 3 is required but not installed"
        log_info "Please install Python 3: brew install python3"
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
        log_error "Python 3.7+ required, found $python_version"
        exit 1
    fi
    
    log_success "System requirements met (Python $python_version)"
}

# Function to validate target drive
validate_target_drive() {
    if [ -z "$TARGET_DRIVE" ]; then
        log_error "Please specify target drive path"
        echo "Usage: $0 /path/to/external/drive"
        echo "Example: $0 /Volumes/MyDrive"
        exit 1
    fi
    
    if [ ! -d "$TARGET_DRIVE" ]; then
        log_error "Target drive not found: $TARGET_DRIVE"
        exit 1
    fi
    
    # Check write permissions
    if [ ! -w "$TARGET_DRIVE" ]; then
        log_error "No write permission to target drive: $TARGET_DRIVE"
        exit 1
    fi
    
    # Check available space (need at least 100MB)
    available_space=$(df -m "$TARGET_DRIVE" | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 100 ]; then
        log_error "Insufficient space on drive (need at least 100MB, found ${available_space}MB)"
        exit 1
    fi
    
    log_success "Target drive validated: $TARGET_DRIVE"
}

# Function to install Python dependencies
install_python_deps() {
    log_step "Installing Python dependencies..."
    
    # Check if psutil is available
    if ! python3 -c "import psutil" >/dev/null 2>&1; then
        log_info "Installing psutil for system monitoring..."
        pip3 install psutil --user --quiet || {
            log_warning "Failed to install psutil automatically"
            log_info "You can install manually: pip3 install psutil"
        }
    fi
    
    log_success "Python dependencies ready"
}

# Function to install optional tools
install_optional_tools() {
    log_step "Checking optional tools..."
    
    # Check for Homebrew
    if command -v brew >/dev/null 2>&1; then
        log_info "Homebrew found, checking optional tools..."
        
        # ExifTool for enhanced photo metadata
        if ! command -v exiftool >/dev/null 2>&1; then
            log_info "Installing exiftool for enhanced photo processing..."
            brew install exiftool --quiet || log_warning "Failed to install exiftool"
        fi
        
        # FFmpeg for video processing
        if ! command -v ffmpeg >/dev/null 2>&1; then
            log_info "Installing ffmpeg for video processing..."
            brew install ffmpeg --quiet || log_warning "Failed to install ffmpeg"
        fi
        
        # smartctl for drive health monitoring
        if ! command -v smartctl >/dev/null 2>&1; then
            log_info "Installing smartmontools for drive health..."
            brew install smartmontools --quiet || log_warning "Failed to install smartmontools"
        fi
        
    else
        log_warning "Homebrew not found - optional tools will be skipped"
        log_info "Install Homebrew for enhanced features: https://brew.sh"
    fi
    
    log_success "Optional tools check complete"
}

# Function to create directory structure
create_directories() {
    log_step "Creating directory structure..."
    
    # Main directories
    directories=(
        "Scripts"
        "Templates"
        "Personal/You"
        "Personal/Wife"
        "Work/You"
        "Work/Wife"
        "Media/Photos/Raw"
        "Media/Photos/Edited"
        "Media/Photos/2024"
        "Media/Photos/2025"
        "Media/Videos/Raw Footage"
        "Media/Videos/Projects"
        "Media/Videos/Home Movies"
        "Media/Music/Library"
        "Media/Music/Playlists"
        "Creative/Art & Design"
        "Creative/Writing"
        "Creative/Music"
        "Creative/Video Projects"
        "Learning/Courses"
        "Learning/Books & PDFs"
        "Learning/Tutorials"
        "Shared/Household/Bills & Finance"
        "Shared/Household/Insurance & Legal"
        "Shared/Travel/Trip Planning"
        "Shared/Entertainment/Movies"
        "Shared/Reference/Manuals & Guides"
        "Backups/MacBook/Documents"
        "Backups/Phone Backups/You"
        "Backups/Phone Backups/Wife"
        "Archive/Old Projects"
        "Archive/Old Photos"
        "Software/Applications"
        "Software/Installers"
        "Temp/Downloads"
        "Temp/Works in Progress"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$TARGET_DRIVE/$dir"
    done
    
    log_success "Directory structure created"
}

# Function to copy files
copy_files() {
    log_step "Copying system files..."
    
    # Copy all scripts
    if [ -d "$SCRIPT_DIR/Scripts" ]; then
        cp -R "$SCRIPT_DIR/Scripts/"* "$TARGET_DRIVE/Scripts/"
        log_success "Scripts copied"
    fi
    
    # Copy templates
    if [ -d "$SCRIPT_DIR/Templates" ]; then
        cp -R "$SCRIPT_DIR/Templates/"* "$TARGET_DRIVE/Templates/"
        log_success "Templates copied"
    fi
    
    # Copy documentation
    if [ -f "$SCRIPT_DIR/README.md" ]; then
        cp "$SCRIPT_DIR/README.md" "$TARGET_DRIVE/"
        log_success "Documentation copied"
    fi
    
    # Copy quick start guide
    if [ -f "$SCRIPT_DIR/QUICK-START.txt" ]; then
        cp "$SCRIPT_DIR/QUICK-START.txt" "$TARGET_DRIVE/🎯-QUICK-START.txt"
    fi
    
    # Make all scripts executable
    find "$TARGET_DRIVE/Scripts" -name "*.sh" -exec chmod +x {} \;
    find "$TARGET_DRIVE/Scripts" -name "*.py" -exec chmod +x {} \;
    
    log_success "Files copied and permissions set"
}

# Function to configure system
configure_system() {
    log_step "Configuring system..."
    
    # Update paths in scripts to use the actual drive path
    if [ -f "$TARGET_DRIVE/Scripts/setup_aliases.sh" ]; then
        # Update drive path in aliases script
        sed -i '' "s|/Volumes/Seagate 2TB|$TARGET_DRIVE|g" "$TARGET_DRIVE/Scripts/setup_aliases.sh"
    fi
    
    # Update other scripts with correct paths
    find "$TARGET_DRIVE/Scripts" -name "*.py" -exec sed -i '' "s|/Volumes/Seagate 2TB|$TARGET_DRIVE|g" {} \;
    find "$TARGET_DRIVE/Scripts" -name "*.sh" -exec sed -i '' "s|/Volumes/Seagate 2TB|$TARGET_DRIVE|g" {} \;
    
    # Create initial configuration
    cat > "$TARGET_DRIVE/.drive_config" << EOF
# 🎯 MASTER CONTROL CENTER CONFIGURATION
DRIVE_NAME="Master Control Center Drive"
SETUP_DATE="$(date '+%Y-%m-%d')"
VERSION="1.0.0"
INSTALL_PATH="$TARGET_DRIVE"

# System settings
AUTO_ORGANIZE_ENABLED=true
AUTO_BACKUP_INTERVAL="weekly"
CLEANUP_TEMP_DAYS=30

# Feature flags
SMART_SORTING=true
AUTO_DUPLICATE_DETECTION=true
PHOTO_DATE_EXTRACTION=true
VIDEO_TRANSCODING=false
EOF
    
    log_success "System configured"
}

# Function to run initial setup
run_initial_setup() {
    log_step "Running initial setup..."
    
    # Run the aliases setup
    if [ -f "$TARGET_DRIVE/Scripts/setup_aliases.sh" ]; then
        log_info "Setting up terminal aliases..."
        bash "$TARGET_DRIVE/Scripts/setup_aliases.sh" || log_warning "Alias setup failed - run manually later"
    fi
    
    # Initialize search index
    if [ -f "$TARGET_DRIVE/Scripts/smart_search.py" ]; then
        log_info "Initializing search system..."
        python3 "$TARGET_DRIVE/Scripts/smart_search.py" index --rebuild >/dev/null 2>&1 || log_warning "Search index initialization failed"
    fi
    
    log_success "Initial setup complete"
}

# Function to display completion message
show_completion() {
    echo ""
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 INSTALLATION COMPLETE!                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}Your drive is now a productivity powerhouse! 🚀${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "  1. ${GREEN}source ~/.zshrc${NC} or ${GREEN}source ~/.bash_profile${NC} (reload terminal)"
    echo -e "  2. ${GREEN}drivedash${NC} - View system dashboard"
    echo -e "  3. ${GREEN}driveauto${NC} - Run full automation"
    echo ""
    echo -e "${YELLOW}Available commands:${NC}"
    echo -e "  ${GREEN}drivehelp${NC}     - Show all commands"
    echo -e "  ${GREEN}organize${NC}      - Smart file organization"
    echo -e "  ${GREEN}backup${NC}        - Intelligent backup"
    echo -e "  ${GREEN}finddupes${NC}     - Find duplicate files"
    echo -e "  ${GREEN}drivehealth${NC}   - Drive health monitoring"
    echo -e "  ${GREEN}projectmgr${NC}    - Project management"
    echo -e "  ${GREEN}smartsearch${NC}   - AI-powered search"
    echo ""
    echo -e "${BLUE}Installation location: ${BOLD}$TARGET_DRIVE${NC}"
    echo -e "${BLUE}Quick start guide: ${BOLD}$TARGET_DRIVE/🎯-QUICK-START.txt${NC}"
    echo ""
    echo -e "${PURPLE}Happy organizing! 🎛️${NC}"
}

# Main installation function
main() {
    # Parse arguments
    TARGET_DRIVE="$1"
    
    # Print banner
    print_banner
    
    # Run installation steps
    check_requirements
    validate_target_drive
    install_python_deps
    install_optional_tools
    create_directories
    copy_files
    configure_system
    run_initial_setup
    show_completion
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi