#!/bin/bash

# 🎬 ADVANCED MEDIA PROCESSOR
# AI-powered media organization and optimization

DRIVE_PATH="/Volumes/Seagate 2TB"
MEDIA_PATH="$DRIVE_PATH/Media"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    
    printf "\r${BLUE}["
    for ((i=0; i<completed; i++)); do printf "█"; done
    for ((i=completed; i<width; i++)); do printf " "; done
    printf "] %d%% (%d/%d)${NC}" "$percentage" "$current" "$total"
}

# Extract EXIF data from photos and organize by date
smart_photo_sort() {
    echo -e "${PURPLE}📸 Starting intelligent photo organization...${NC}"
    
    local count=0
    local total=$(find "$MEDIA_PATH/Photos/Raw" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.heic" \) | wc -l | xargs)
    
    if [ "$total" -eq 0 ]; then
        echo -e "${YELLOW}No photos found in Raw folder${NC}"
        return
    fi
    
    find "$MEDIA_PATH/Photos/Raw" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.heic" \) | while read -r file; do
        ((count++))
        show_progress "$count" "$total"
        
        # Extract date from EXIF (requires exiftool - install with brew install exiftool)
        if command -v exiftool >/dev/null; then
            date_taken=$(exiftool -DateTimeOriginal -d "%Y-%m" "$file" 2>/dev/null | grep -o "[0-9]\{4\}-[0-9]\{2\}")
            if [[ -n "$date_taken" ]]; then
                year=$(echo "$date_taken" | cut -d'-' -f1)
                month=$(echo "$date_taken" | cut -d'-' -f2)
                month_name=$(date -j -f "%m" "$month" "+%B" 2>/dev/null || echo "$month")
                
                dest_dir="$MEDIA_PATH/Photos/$year/$month-$month_name"
                mkdir -p "$dest_dir"
                mv "$file" "$dest_dir/"
            fi
        else
            # Fallback: organize by file modification date
            file_date=$(stat -f "%Sm" -t "%Y-%m" "$file")
            year=$(echo "$file_date" | cut -d'-' -f1)
            month=$(echo "$file_date" | cut -d'-' -f2)
            month_name=$(date -j -f "%m" "$month" "+%B" 2>/dev/null || echo "$month")
            
            dest_dir="$MEDIA_PATH/Photos/$year/$month-$month_name"
            mkdir -p "$dest_dir"
            mv "$file" "$dest_dir/"
        fi
    done
    
    echo -e "\n${GREEN}✅ Photos organized by date!${NC}"
}

# Compress large video files
optimize_videos() {
    echo -e "${CYAN}🎬 Starting video optimization...${NC}"
    
    # Check if ffmpeg is available
    if ! command -v ffmpeg >/dev/null; then
        echo -e "${RED}❌ ffmpeg not found. Install with: brew install ffmpeg${NC}"
        return 1
    fi
    
    local count=0
    local total=$(find "$MEDIA_PATH/Videos/Raw Footage" -type f \( -iname "*.mov" -o -iname "*.mp4" -o -iname "*.avi" \) | wc -l | xargs)
    
    find "$MEDIA_PATH/Videos/Raw Footage" -type f \( -iname "*.mov" -o -iname "*.mp4" -o -iname "*.avi" \) | while read -r file; do
        ((count++))
        show_progress "$count" "$total"
        
        # Get file size in MB
        size_mb=$(du -m "$file" | cut -f1)
        
        # Compress videos larger than 100MB
        if [ "$size_mb" -gt 100 ]; then
            filename=$(basename "$file" | sed 's/\.[^.]*$//')
            extension="${file##*.}"
            optimized_file="$MEDIA_PATH/Videos/Projects/${filename}_optimized.mp4"
            
            # Compress with H.264, maintaining quality
            ffmpeg -i "$file" -c:v libx264 -crf 23 -c:a aac -b:a 128k "$optimized_file" -y >/dev/null 2>&1
            
            if [ $? -eq 0 ]; then
                # Move original to archive if compression successful
                mkdir -p "$DRIVE_PATH/Archive/Original Videos"
                mv "$file" "$DRIVE_PATH/Archive/Original Videos/"
            fi
        fi
    done
    
    echo -e "\n${GREEN}✅ Video optimization complete!${NC}"
}

# Create video thumbnails
generate_thumbnails() {
    echo -e "${BLUE}🖼️  Generating video thumbnails...${NC}"
    
    if ! command -v ffmpeg >/dev/null; then
        echo -e "${RED}❌ ffmpeg not found${NC}"
        return 1
    fi
    
    mkdir -p "$MEDIA_PATH/Videos/.thumbnails"
    
    find "$MEDIA_PATH/Videos" -name "*.mp4" -o -name "*.mov" -o -name "*.avi" | while read -r video; do
        thumb_name=$(basename "$video" | sed 's/\.[^.]*$/.jpg/')
        thumb_path="$MEDIA_PATH/Videos/.thumbnails/$thumb_name"
        
        if [ ! -f "$thumb_path" ]; then
            # Generate thumbnail at 10% of video duration
            duration=$(ffprobe -i "$video" -show_entries format=duration -v quiet -of csv="p=0")
            seek_time=$(echo "$duration * 0.1" | bc 2>/dev/null || echo "5")
            
            ffmpeg -i "$video" -ss "$seek_time" -vframes 1 -q:v 2 "$thumb_path" -y >/dev/null 2>&1
        fi
    done
    
    echo -e "${GREEN}✅ Thumbnails generated!${NC}"
}

# Audio analysis and tagging
analyze_music() {
    echo -e "${PURPLE}🎵 Analyzing music library...${NC}"
    
    local stats_file="$MEDIA_PATH/Music/.library_stats.txt"
    echo "Music Library Analysis - $(date)" > "$stats_file"
    echo "=================================" >> "$stats_file"
    
    # Count files by format
    echo "File Formats:" >> "$stats_file"
    for ext in mp3 m4a wav flac aac; do
        count=$(find "$MEDIA_PATH/Music" -iname "*.$ext" | wc -l | xargs)
        echo "  $ext: $count files" >> "$stats_file"
    done
    
    # Total size
    total_size=$(du -sh "$MEDIA_PATH/Music" | cut -f1)
    echo "Total Size: $total_size" >> "$stats_file"
    
    # Create genre folders based on file names
    mkdir -p "$MEDIA_PATH/Music/Library/Rock" "$MEDIA_PATH/Music/Library/Pop" "$MEDIA_PATH/Music/Library/Classical" "$MEDIA_PATH/Music/Library/Electronic"
    
    echo -e "${GREEN}✅ Music analysis complete! Check $stats_file${NC}"
}

# Main menu
case "$1" in
    "photos")
        smart_photo_sort
        ;;
    "videos")
        optimize_videos
        generate_thumbnails
        ;;
    "music")
        analyze_music
        ;;
    "thumbnails")
        generate_thumbnails
        ;;
    "all")
        echo -e "${PURPLE}🚀 Starting complete media processing...${NC}"
        smart_photo_sort
        echo ""
        optimize_videos
        echo ""
        generate_thumbnails
        echo ""
        analyze_music
        echo -e "${GREEN}🎉 All media processing complete!${NC}"
        ;;
    *)
        echo -e "${PURPLE}🎬 ADVANCED MEDIA PROCESSOR${NC}"
        echo -e "${CYAN}================================${NC}"
        echo -e "${GREEN}Usage: $0 {photos|videos|music|thumbnails|all}${NC}"
        echo -e "  ${YELLOW}photos${NC}     - Smart photo organization by date"
        echo -e "  ${YELLOW}videos${NC}     - Compress and optimize videos"
        echo -e "  ${YELLOW}music${NC}      - Analyze and organize music"
        echo -e "  ${YELLOW}thumbnails${NC} - Generate video thumbnails"
        echo -e "  ${YELLOW}all${NC}        - Run complete media processing"
        echo ""
        echo -e "${BLUE}Requirements:${NC}"
        echo -e "  • exiftool (brew install exiftool)"
        echo -e "  • ffmpeg (brew install ffmpeg)"
        ;;
esac