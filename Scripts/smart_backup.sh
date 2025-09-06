#!/bin/bash

# 🔄 SMART BACKUP SYSTEM
# Automatically sync MacBook to external drive with intelligence

MACBOOK_HOME="$HOME"
BACKUP_ROOT="/Volumes/Seagate 2TB/Backups/MacBook"
LOG_FILE="/Volumes/Seagate 2TB/Scripts/backup.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging function
log() {
    echo "$(date): $1" >> "$LOG_FILE"
    echo -e "$1"
}

# Smart backup function
smart_backup() {
    log "${BLUE}🚀 Starting smart backup...${NC}"
    
    # Backup Documents (excluding temp files)
    rsync -av --delete --exclude="*.tmp" --exclude=".DS_Store" \
          "$MACBOOK_HOME/Documents/" "$BACKUP_ROOT/Documents/" \
          && log "${GREEN}✅ Documents backed up${NC}" \
          || log "${RED}❌ Documents backup failed${NC}"
    
    # Backup Desktop (excluding system files)
    rsync -av --delete --exclude=".DS_Store" --exclude="*.tmp" \
          "$MACBOOK_HOME/Desktop/" "$BACKUP_ROOT/Desktop/" \
          && log "${GREEN}✅ Desktop backed up${NC}" \
          || log "${RED}❌ Desktop backup failed${NC}"
    
    # Backup specific Applications (user-installed)
    if [ -d "$MACBOOK_HOME/Applications" ]; then
        rsync -av "$MACBOOK_HOME/Applications/" "$BACKUP_ROOT/Applications/" \
              && log "${GREEN}✅ Applications backed up${NC}"
    fi
    
    # Create backup manifest
    echo "Backup completed: $(date)" > "$BACKUP_ROOT/BACKUP_MANIFEST.txt"
    echo "Total size: $(du -sh "$BACKUP_ROOT" | cut -f1)" >> "$BACKUP_ROOT/BACKUP_MANIFEST.txt"
    
    log "${YELLOW}📝 Backup manifest created${NC}"
}

# Quick backup for specific folders
quick_backup() {
    case "$1" in
        "photos")
            rsync -av "$MACBOOK_HOME/Pictures/" "/Volumes/Seagate 2TB/Media/Photos/Raw/"
            log "${GREEN}📸 Photos synced${NC}"
            ;;
        "music")
            rsync -av "$MACBOOK_HOME/Music/iTunes/iTunes Media/Music/" "/Volumes/Seagate 2TB/Media/Music/Library/"
            log "${GREEN}🎵 Music synced${NC}"
            ;;
        "videos")
            rsync -av "$MACBOOK_HOME/Movies/" "/Volumes/Seagate 2TB/Media/Videos/Raw Footage/"
            log "${GREEN}🎬 Videos synced${NC}"
            ;;
    esac
}

# Main execution
case "$1" in
    "full")
        smart_backup
        ;;
    "photos"|"music"|"videos")
        quick_backup "$1"
        ;;
    *)
        echo -e "${BLUE}🔄 SMART BACKUP SYSTEM${NC}"
        echo -e "${GREEN}Usage: $0 {full|photos|music|videos}${NC}"
        echo -e "  full   - Complete MacBook backup"
        echo -e "  photos - Sync photos only"
        echo -e "  music  - Sync music only"
        echo -e "  videos - Sync videos only"
        ;;
esac