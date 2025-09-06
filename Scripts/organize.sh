#!/bin/bash

# 🚀 ULTIMATE FILE ORGANIZER SCRIPT
# Custom organization system for your 2TB drive

DRIVE_PATH="/Volumes/Seagate 2TB"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🎯 Starting intelligent file organization...${NC}"

# Function to organize downloads by file type
organize_downloads() {
    echo -e "${BLUE}📁 Organizing downloads...${NC}"
    
    TEMP_DIR="$DRIVE_PATH/Temp/Downloads"
    
    # Images
    find "$TEMP_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.raw" -o -iname "*.heic" \) -exec mv {} "$DRIVE_PATH/Media/Photos/Raw/" \; 2>/dev/null
    
    # Videos
    find "$TEMP_DIR" -type f \( -iname "*.mp4" -o -iname "*.mov" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.m4v" \) -exec mv {} "$DRIVE_PATH/Media/Videos/Raw Footage/" \; 2>/dev/null
    
    # Music
    find "$TEMP_DIR" -type f \( -iname "*.mp3" -o -iname "*.m4a" -o -iname "*.wav" -o -iname "*.flac" -o -iname "*.aac" \) -exec mv {} "$DRIVE_PATH/Media/Music/Library/" \; 2>/dev/null
    
    # Documents
    find "$TEMP_DIR" -type f \( -iname "*.pdf" -o -iname "*.doc" -o -iname "*.docx" -o -iname "*.txt" -o -iname "*.rtf" \) -exec mv {} "$DRIVE_PATH/Learning/Books & PDFs/" \; 2>/dev/null
    
    # Software
    find "$TEMP_DIR" -type f \( -iname "*.dmg" -o -iname "*.pkg" -o -iname "*.app" -o -iname "*.zip" \) -exec mv {} "$DRIVE_PATH/Software/Installers/" \; 2>/dev/null
    
    echo -e "${GREEN}✅ Downloads organized!${NC}"
}

# Function to clean up empty directories
cleanup_empty_dirs() {
    echo -e "${YELLOW}🧹 Cleaning up empty directories...${NC}"
    find "$DRIVE_PATH" -type d -empty -delete 2>/dev/null
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
}

# Function to generate storage report
storage_report() {
    echo -e "${PURPLE}📊 Storage Report:${NC}"
    echo -e "${BLUE}==================${NC}"
    
    for dir in "Media" "Work" "Backups" "Creative" "Learning" "Shared"; do
        if [ -d "$DRIVE_PATH/$dir" ]; then
            size=$(du -sh "$DRIVE_PATH/$dir" | cut -f1)
            echo -e "${GREEN}$dir: $size${NC}"
        fi
    done
    
    echo -e "${BLUE}==================${NC}"
    total=$(df -h "$DRIVE_PATH" | tail -1 | awk '{print $3 " used of " $2}')
    echo -e "${YELLOW}Total: $total${NC}"
}

# Main menu
case "$1" in
    "downloads")
        organize_downloads
        ;;
    "cleanup")
        cleanup_empty_dirs
        ;;
    "report")
        storage_report
        ;;
    "all")
        organize_downloads
        cleanup_empty_dirs
        storage_report
        ;;
    *)
        echo -e "${PURPLE}🎯 ULTIMATE FILE ORGANIZER${NC}"
        echo -e "${BLUE}Usage: $0 {downloads|cleanup|report|all}${NC}"
        echo -e "${GREEN}  downloads - Sort downloads into proper folders${NC}"
        echo -e "${GREEN}  cleanup   - Remove empty directories${NC}"
        echo -e "${GREEN}  report    - Show storage usage${NC}"
        echo -e "${GREEN}  all       - Run everything${NC}"
        ;;
esac