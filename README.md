# 🎛️ Master Control Center
### The Ultimate External Drive Management System

> Transform any external drive into an AI-powered productivity ecosystem with automated organization, intelligent backups, and advanced file management.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🚀 What Makes This Special?

This isn't just file organization - it's a complete **AI-powered productivity operating system** for your external drive:

### 🔥 Core Features

- **🔍 Intelligent Duplicate Detection** - ML-powered duplicate finder with conflict resolution
- **🛡️ Drive Health Guardian** - Real-time monitoring with SMART data analysis  
- **🎯 Project Lifecycle Manager** - Complete project management with automated structures
- **🔍 Smart Search Engine** - AI-powered file search with content indexing
- **☁️ Multi-Cloud Sync** - Intelligent synchronization with conflict resolution
- **🎬 Advanced Media Processing** - Photo organization, video compression, thumbnail generation
- **🎛️ Master Control Dashboard** - Unified interface for all systems

### ⚡ Instant Productivity

- **20+ Terminal Aliases** for lightning-fast access
- **Automated Maintenance** sequences
- **Smart File Organization** by type, date, and content
- **Intelligent Backup System** with exclusions
- **Progress Tracking** with visual indicators
- **Desktop Shortcuts** for common operations

## 📦 Installation

### Quick Install
```bash
# Clone the repository
git clone https://github.com/Thatkidtk/Master-Control-Center.git

# Run the installer
cd Master-Control-Center
./install.sh /path/to/your/external/drive
```

### Manual Install
```bash
# Copy all files to your drive
cp -r Scripts/ /Volumes/YourDrive/
cp -r Templates/ /Volumes/YourDrive/
cp README.md /Volumes/YourDrive/

# Setup terminal aliases
./Scripts/setup_aliases.sh

# Run the master control center
python3 /Volumes/YourDrive/Scripts/master_control.py dashboard
```

## 🎯 Quick Start

1. **Setup Aliases** - Run `./Scripts/setup_aliases.sh` for terminal shortcuts
2. **View Dashboard** - Type `drivedash` to see system overview
3. **Run Automation** - Type `driveauto` for full maintenance sequence

### Essential Commands

```bash
# System Management
drivedash           # System dashboard and overview
driveauto           # Run full automation sequence
drivehelp           # Show all available commands

# File Operations  
organize            # Smart file organization
backup              # Intelligent backup system
finddupes           # Find and clean duplicate files

# Advanced Features
drivehealth         # Drive health monitoring
projectmgr          # Project management system
smartsearch         # AI-powered file search
cloudsync           # Multi-cloud synchronization
```

## 🎛️ System Components

### 🔧 Core Scripts

| Script | Description | Key Features |
|--------|-------------|--------------|
| `master_control.py` | Unified control center | Dashboard, automation, system orchestration |
| `organize.sh` | File organization | Smart sorting, cleanup, storage reports |
| `smart_backup.sh` | Intelligent backup | Selective sync, exclusion patterns, logging |

### 🐍 Python-Powered Systems

| System | Description | Advanced Features |
|--------|-------------|-------------------|
| `duplicate_hunter.py` | Duplicate detection | ML recommendations, interactive cleanup, conflict resolution |
| `drive_guardian.py` | Health monitoring | SMART data analysis, automated alerts, trend tracking |
| `project_manager.py` | Project management | Lifecycle tracking, automated structures, progress visualization |
| `smart_search.py` | File search engine | Content indexing, AI tagging, relevance ranking |
| `cloud_sync.py` | Multi-cloud sync | Conflict resolution, intelligent merging, status tracking |
| `media_processor.sh` | Media automation | EXIF extraction, video compression, thumbnail generation |

## 📁 Directory Structure

```
YourDrive/
├── Scripts/                 # All automation scripts
│   ├── master_control.py   # Main control center
│   ├── *.py               # Python systems
│   └── *.sh               # Shell scripts
├── Templates/              # Project templates
├── Personal/              # Individual workspaces  
├── Work/                  # Professional projects
├── Media/                 # Organized media library
├── Creative/              # Creative projects
├── Shared/                # Household organization
├── Backups/               # System backups
├── Archive/               # Long-term storage
└── Temp/                  # Temporary workspace
```

## 🔧 Advanced Usage

### Project Management
```bash
# Create a new project
projectmgr create "Website Redesign" --type web --owner You

# List all projects  
projectmgr list --status active

# Update project progress
projectmgr update --id abc12345 --progress 75
```

### Smart Search
```bash
# Build search index
smartsearch index

# Search with AI
smartsearch search "budget spreadsheet 2024"

# Search by file type
smartsearch search "presentation" --type document
```

### Duplicate Management
```bash
# Interactive duplicate cleanup
finddupes --interactive

# Generate duplicate report
finddupes --report duplicates.json

# Scan specific extensions only  
finddupes --extensions .jpg .png .mp4
```

### Health Monitoring
```bash
# Check drive health
drivehealth

# View configuration
drivehealth --config

# Historical health data available in Scripts/health_history.json
```

## 🛠️ Requirements

### System Requirements
- **macOS** 10.14+ (Mojave or later)
- **Python** 3.7 or higher
- **External Drive** with at least 1GB free space

### Optional Dependencies (Auto-installed)
- `exiftool` - Enhanced photo metadata extraction
- `ffmpeg` - Video processing and compression  
- `smartctl` - Drive health monitoring
- `pdftotext` - PDF content indexing

### Python Packages
```bash
pip3 install psutil      # Drive statistics
pip3 install sqlite3     # Search indexing (usually included)
```

## 🎨 Customization

### Configuration Files
- `Scripts/.drive_config` - Main system settings
- `Scripts/search_config.json` - Search preferences  
- `Scripts/cloud_sync_config.json` - Cloud synchronization
- `Scripts/.guardian_config.json` - Health monitoring

### Adding Custom Scripts
1. Place scripts in `Scripts/` directory
2. Add to `master_control.py` systems dictionary
3. Update aliases in `setup_aliases.sh`

### Custom Project Templates
Add new templates to `Templates/` directory with `.md` files.

## 📊 System Monitoring

### Health Dashboard
- **Drive Usage** - Real-time storage statistics
- **File Counts** - Organized by category
- **System Status** - All components health
- **Recent Activity** - Sync history and operations

### Automated Alerts
- Storage space warnings (85%+ usage)
- Large temporary file accumulation
- Duplicate file detection
- Drive health anomalies

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/Thatkidtk/Master-Control-Center.git
cd Master-Control-Center
./dev-setup.sh
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Claude Code** - AI-assisted development
- **Python Community** - Amazing libraries and tools
- **macOS Community** - System integration insights
- **Open Source Contributors** - Inspiration and best practices

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Thatkidtk/Master-Control-Center/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Thatkidtk/Master-Control-Center/discussions)
- **Wiki**: [Project Wiki](https://github.com/Thatkidtk/Master-Control-Center/wiki)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Thatkidtk/Master-Control-Center&type=Date)](https://star-history.com/#Thatkidtk/Master-Control-Center&Date)

---

### 🚀 Ready to Transform Your External Drive?

**[Install Now](#installation)** and turn any external drive into a productivity powerhouse!

> *"This isn't just storage - it's an AI-powered productivity ecosystem!"*