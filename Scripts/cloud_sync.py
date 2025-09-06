#!/usr/bin/env python3
"""
☁️ CLOUD SYNC INTEGRATION SYSTEM
Multi-platform cloud synchronization with intelligent conflict resolution
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import argparse

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class CloudSync:
    def __init__(self, drive_path="/Volumes/Seagate 2TB"):
        self.drive_path = Path(drive_path)
        self.config_path = self.drive_path / "Scripts" / "cloud_sync_config.json"
        self.state_path = self.drive_path / "Scripts" / "sync_state.json"
        self.log_path = self.drive_path / "Scripts" / "sync.log"
        
        self.config = self.load_config()
        self.sync_state = self.load_sync_state()
        self.running = False
    
    def load_config(self):
        """Load synchronization configuration"""
        default_config = {
            "providers": {
                "dropbox": {
                    "enabled": False,
                    "local_path": "/Users/{user}/Dropbox",
                    "sync_folders": ["Documents", "Photos"],
                    "exclude_patterns": [".DS_Store", "*.tmp", "*.temp"]
                },
                "google_drive": {
                    "enabled": False,
                    "local_path": "/Users/{user}/Google Drive",
                    "sync_folders": ["Work", "Creative"],
                    "exclude_patterns": [".DS_Store", "*.tmp", "*.temp"]
                },
                "icloud": {
                    "enabled": False,
                    "local_path": "/Users/{user}/Library/Mobile Documents/com~apple~CloudDocs",
                    "sync_folders": ["Personal"],
                    "exclude_patterns": [".DS_Store", "*.tmp", "*.temp"]
                },
                "onedrive": {
                    "enabled": False,
                    "local_path": "/Users/{user}/OneDrive",
                    "sync_folders": ["Shared"],
                    "exclude_patterns": [".DS_Store", "*.tmp", "*.temp"]
                }
            },
            "sync_settings": {
                "check_interval_minutes": 30,
                "max_file_size_mb": 1000,
                "conflict_resolution": "newest",  # newest, ask, rename
                "backup_conflicts": True,
                "sync_deletions": False,
                "dry_run": False
            },
            "notifications": {
                "enabled": True,
                "on_sync_complete": True,
                "on_conflicts": True,
                "on_errors": True
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Deep merge
                    for category in default_config:
                        if category in loaded_config:
                            if isinstance(default_config[category], dict):
                                default_config[category].update(loaded_config[category])
                            else:
                                default_config[category] = loaded_config[category]
                return default_config
            except json.JSONDecodeError:
                pass
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def load_sync_state(self):
        """Load synchronization state"""
        if self.sync_state_path.exists():
            try:
                with open(self.sync_state_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        return {
            "last_sync": {},
            "file_hashes": {},
            "conflicts": [],
            "sync_history": []
        }
    
    def save_sync_state(self):
        """Save synchronization state"""
        with open(self.state_path, 'w') as f:
            json.dump(self.sync_state, f, indent=2, default=str)
    
    def log_message(self, message, level="INFO"):
        """Log sync messages"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        with open(self.log_path, 'a') as f:
            f.write(log_entry)
        
        # Also print to console
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED
        }
        color = colors.get(level, Colors.WHITE)
        print(f"{color}[{level}] {message}{Colors.END}")
    
    def calculate_file_hash(self, filepath):
        """Calculate MD5 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return None
    
    def should_exclude_file(self, filepath, exclude_patterns):
        """Check if file should be excluded from sync"""
        filename = filepath.name
        
        for pattern in exclude_patterns:
            if pattern.startswith('*.'):
                extension = pattern[1:]
                if filename.endswith(extension):
                    return True
            elif pattern in filename:
                return True
        
        return False
    
    def find_sync_candidates(self, provider_name, provider_config):
        """Find files that need synchronization"""
        candidates = {
            "to_cloud": [],    # Files to upload to cloud
            "from_cloud": [],  # Files to download from cloud
            "conflicts": []    # Files with conflicts
        }
        
        cloud_path = Path(provider_config["local_path"].replace("{user}", os.getenv("USER", "")))
        
        if not cloud_path.exists():
            self.log_message(f"Cloud path not found: {cloud_path}", "WARNING")
            return candidates
        
        for folder_name in provider_config["sync_folders"]:
            drive_folder = self.drive_path / folder_name
            cloud_folder = cloud_path / folder_name
            
            if not drive_folder.exists():
                continue
            
            # Scan drive folder
            for root, dirs, files in os.walk(drive_folder):
                for file in files:
                    drive_file = Path(root) / file
                    
                    if self.should_exclude_file(drive_file, provider_config["exclude_patterns"]):
                        continue
                    
                    # Calculate relative path
                    rel_path = drive_file.relative_to(drive_folder)
                    cloud_file = cloud_folder / rel_path
                    
                    # Check if file exists in cloud
                    if cloud_file.exists():
                        # Compare modification times and hashes
                        drive_stat = drive_file.stat()
                        cloud_stat = cloud_file.stat()
                        
                        drive_hash = self.calculate_file_hash(drive_file)
                        cloud_hash = self.calculate_file_hash(cloud_file)
                        
                        if drive_hash != cloud_hash:
                            # Conflict detected
                            candidates["conflicts"].append({
                                "drive_file": str(drive_file),
                                "cloud_file": str(cloud_file),
                                "drive_modified": drive_stat.st_mtime,
                                "cloud_modified": cloud_stat.st_mtime,
                                "drive_hash": drive_hash,
                                "cloud_hash": cloud_hash
                            })
                    else:
                        # File only exists on drive - upload to cloud
                        cloud_file.parent.mkdir(parents=True, exist_ok=True)
                        candidates["to_cloud"].append({
                            "source": str(drive_file),
                            "destination": str(cloud_file)
                        })
            
            # Scan cloud folder for files not on drive
            if cloud_folder.exists():
                for root, dirs, files in os.walk(cloud_folder):
                    for file in files:
                        cloud_file = Path(root) / file
                        
                        if self.should_exclude_file(cloud_file, provider_config["exclude_patterns"]):
                            continue
                        
                        rel_path = cloud_file.relative_to(cloud_folder)
                        drive_file = drive_folder / rel_path
                        
                        if not drive_file.exists():
                            # File only exists in cloud - download to drive
                            drive_file.parent.mkdir(parents=True, exist_ok=True)
                            candidates["from_cloud"].append({
                                "source": str(cloud_file),
                                "destination": str(drive_file)
                            })
        
        return candidates
    
    def resolve_conflict(self, conflict):
        """Resolve sync conflict based on configuration"""
        resolution_strategy = self.config["sync_settings"]["conflict_resolution"]
        
        drive_file = Path(conflict["drive_file"])
        cloud_file = Path(conflict["cloud_file"])
        
        if resolution_strategy == "newest":
            # Keep the newer file
            if conflict["drive_modified"] > conflict["cloud_modified"]:
                # Drive file is newer
                action = "upload_to_cloud"
                source, dest = drive_file, cloud_file
            else:
                # Cloud file is newer
                action = "download_to_drive"
                source, dest = cloud_file, drive_file
        
        elif resolution_strategy == "rename":
            # Rename the older file and keep both
            if conflict["drive_modified"] > conflict["cloud_modified"]:
                # Rename cloud file
                timestamp = datetime.fromtimestamp(conflict["cloud_modified"]).strftime('%Y%m%d_%H%M%S')
                backup_name = f"{cloud_file.stem}_conflict_{timestamp}{cloud_file.suffix}"
                backup_path = cloud_file.parent / backup_name
                cloud_file.rename(backup_path)
                action = "upload_to_cloud"
                source, dest = drive_file, cloud_file
            else:
                # Rename drive file
                timestamp = datetime.fromtimestamp(conflict["drive_modified"]).strftime('%Y%m%d_%H%M%S')
                backup_name = f"{drive_file.stem}_conflict_{timestamp}{drive_file.suffix}"
                backup_path = drive_file.parent / backup_name
                drive_file.rename(backup_path)
                action = "download_to_drive"
                source, dest = cloud_file, drive_file
        
        else:  # ask
            print(f"{Colors.YELLOW}📋 Conflict detected:{Colors.END}")
            print(f"  Drive: {drive_file} (modified: {datetime.fromtimestamp(conflict['drive_modified'])})")
            print(f"  Cloud: {cloud_file} (modified: {datetime.fromtimestamp(conflict['cloud_modified'])})")
            
            choice = input(f"{Colors.CYAN}Choose: (d)rive version, (c)loud version, (r)ename both: {Colors.END}").lower()
            
            if choice == 'd':
                action = "upload_to_cloud"
                source, dest = drive_file, cloud_file
            elif choice == 'c':
                action = "download_to_drive"
                source, dest = cloud_file, drive_file
            elif choice == 'r':
                return self.resolve_conflict({**conflict, "resolution": "rename"})
            else:
                self.log_message(f"Skipping conflict for {drive_file}", "WARNING")
                return False
        
        # Perform the sync action
        try:
            if self.config["sync_settings"]["backup_conflicts"]:
                # Create backup of destination
                backup_path = dest.parent / f"{dest.stem}_backup_{int(time.time())}{dest.suffix}"
                if dest.exists():
                    dest.rename(backup_path)
            
            # Copy file
            import shutil
            shutil.copy2(source, dest)
            self.log_message(f"Resolved conflict: {source} -> {dest}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message(f"Failed to resolve conflict: {e}", "ERROR")
            return False
    
    def sync_files(self, candidates, dry_run=False):
        """Perform file synchronization"""
        results = {
            "uploaded": 0,
            "downloaded": 0,
            "conflicts_resolved": 0,
            "errors": 0
        }
        
        # Upload files to cloud
        for item in candidates["to_cloud"]:
            try:
                if not dry_run:
                    import shutil
                    shutil.copy2(item["source"], item["destination"])
                    results["uploaded"] += 1
                
                self.log_message(f"{'[DRY RUN] ' if dry_run else ''}Uploaded: {item['source']} -> {item['destination']}", "SUCCESS")
                
            except Exception as e:
                results["errors"] += 1
                self.log_message(f"Upload failed: {item['source']} - {e}", "ERROR")
        
        # Download files from cloud
        for item in candidates["from_cloud"]:
            try:
                if not dry_run:
                    import shutil
                    shutil.copy2(item["source"], item["destination"])
                    results["downloaded"] += 1
                
                self.log_message(f"{'[DRY RUN] ' if dry_run else ''}Downloaded: {item['source']} -> {item['destination']}", "SUCCESS")
                
            except Exception as e:
                results["errors"] += 1
                self.log_message(f"Download failed: {item['source']} - {e}", "ERROR")
        
        # Resolve conflicts
        for conflict in candidates["conflicts"]:
            try:
                if not dry_run:
                    if self.resolve_conflict(conflict):
                        results["conflicts_resolved"] += 1
                    else:
                        results["errors"] += 1
                else:
                    self.log_message(f"[DRY RUN] Would resolve conflict: {conflict['drive_file']}", "INFO")
                
            except Exception as e:
                results["errors"] += 1
                self.log_message(f"Conflict resolution failed: {e}", "ERROR")
        
        return results
    
    def sync_provider(self, provider_name, dry_run=False):
        """Sync with a specific cloud provider"""
        provider_config = self.config["providers"][provider_name]
        
        if not provider_config["enabled"]:
            self.log_message(f"Provider {provider_name} is disabled", "INFO")
            return None
        
        self.log_message(f"Starting sync with {provider_name}", "INFO")
        
        # Find files that need syncing
        candidates = self.find_sync_candidates(provider_name, provider_config)
        
        self.log_message(f"Found {len(candidates['to_cloud'])} files to upload, "
                        f"{len(candidates['from_cloud'])} to download, "
                        f"{len(candidates['conflicts'])} conflicts", "INFO")
        
        # Perform sync
        results = self.sync_files(candidates, dry_run)
        
        # Update sync state
        if not dry_run:
            self.sync_state["last_sync"][provider_name] = datetime.now().isoformat()
            self.sync_state["sync_history"].append({
                "provider": provider_name,
                "timestamp": datetime.now().isoformat(),
                "results": results
            })
            self.save_sync_state()
        
        self.log_message(f"Sync complete - Uploaded: {results['uploaded']}, "
                        f"Downloaded: {results['downloaded']}, "
                        f"Conflicts: {results['conflicts_resolved']}, "
                        f"Errors: {results['errors']}", "SUCCESS")
        
        return results
    
    def sync_all(self, dry_run=False):
        """Sync with all enabled providers"""
        self.log_message("Starting full sync", "INFO")
        
        total_results = {
            "uploaded": 0,
            "downloaded": 0,
            "conflicts_resolved": 0,
            "errors": 0
        }
        
        for provider_name, provider_config in self.config["providers"].items():
            if provider_config["enabled"]:
                results = self.sync_provider(provider_name, dry_run)
                if results:
                    for key in total_results:
                        total_results[key] += results[key]
        
        self.log_message(f"Full sync complete - Total: Uploaded {total_results['uploaded']}, "
                        f"Downloaded {total_results['downloaded']}, "
                        f"Conflicts {total_results['conflicts_resolved']}, "
                        f"Errors {total_results['errors']}", "SUCCESS")
        
        return total_results
    
    def start_daemon(self):
        """Start continuous sync daemon"""
        self.running = True
        interval = self.config["sync_settings"]["check_interval_minutes"] * 60
        
        self.log_message(f"Starting sync daemon (interval: {interval/60} minutes)", "INFO")
        
        while self.running:
            try:
                self.sync_all()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_message(f"Daemon error: {e}", "ERROR")
                time.sleep(60)  # Wait before retrying
        
        self.log_message("Sync daemon stopped", "INFO")
    
    def stop_daemon(self):
        """Stop sync daemon"""
        self.running = False
    
    def show_status(self):
        """Display sync status"""
        print(f"{Colors.BOLD}{Colors.PURPLE}☁️ CLOUD SYNC STATUS{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        # Provider status
        print(f"{Colors.BOLD}📱 Providers:{Colors.END}")
        for name, config in self.config["providers"].items():
            status = f"{Colors.GREEN}Enabled{Colors.END}" if config["enabled"] else f"{Colors.RED}Disabled{Colors.END}"
            last_sync = self.sync_state["last_sync"].get(name, "Never")
            if last_sync != "Never":
                last_sync = datetime.fromisoformat(last_sync).strftime('%Y-%m-%d %H:%M')
            
            print(f"  {name.title()}: {status} | Last sync: {Colors.CYAN}{last_sync}{Colors.END}")
        
        # Recent sync history
        if self.sync_state["sync_history"]:
            print(f"\n{Colors.BOLD}📊 Recent Syncs:{Colors.END}")
            for sync in self.sync_state["sync_history"][-5:]:
                timestamp = datetime.fromisoformat(sync["timestamp"]).strftime('%Y-%m-%d %H:%M')
                results = sync["results"]
                print(f"  {Colors.CYAN}{timestamp}{Colors.END} - {sync['provider']}: "
                      f"↑{results['uploaded']} ↓{results['downloaded']} "
                      f"⚠️{results['conflicts_resolved']} ❌{results['errors']}")
        
        # Configuration
        print(f"\n{Colors.BOLD}⚙️ Settings:{Colors.END}")
        settings = self.config["sync_settings"]
        print(f"  Check interval: {Colors.YELLOW}{settings['check_interval_minutes']} minutes{Colors.END}")
        print(f"  Max file size: {Colors.YELLOW}{settings['max_file_size_mb']} MB{Colors.END}")
        print(f"  Conflict resolution: {Colors.YELLOW}{settings['conflict_resolution']}{Colors.END}")
        print(f"  Dry run mode: {Colors.YELLOW}{settings['dry_run']}{Colors.END}")

def main():
    parser = argparse.ArgumentParser(description='☁️ Cloud Sync Integration')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Sync commands
    sync_parser = subparsers.add_parser('sync', help='Perform sync')
    sync_parser.add_argument('--provider', help='Specific provider to sync')
    sync_parser.add_argument('--dry-run', action='store_true', help='Show what would be synced')
    
    # Daemon commands
    subparsers.add_parser('daemon', help='Start sync daemon')
    subparsers.add_parser('status', help='Show sync status')
    
    # Config commands
    config_parser = subparsers.add_parser('config', help='Configure providers')
    config_parser.add_argument('--enable', help='Enable provider')
    config_parser.add_argument('--disable', help='Disable provider')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    sync_manager = CloudSync()
    
    if args.command == 'sync':
        dry_run = args.dry_run or sync_manager.config["sync_settings"]["dry_run"]
        
        if args.provider:
            sync_manager.sync_provider(args.provider, dry_run)
        else:
            sync_manager.sync_all(dry_run)
    
    elif args.command == 'daemon':
        try:
            sync_manager.start_daemon()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Daemon stopped by user{Colors.END}")
    
    elif args.command == 'status':
        sync_manager.show_status()
    
    elif args.command == 'config':
        if args.enable:
            if args.enable in sync_manager.config["providers"]:
                sync_manager.config["providers"][args.enable]["enabled"] = True
                with open(sync_manager.config_path, 'w') as f:
                    json.dump(sync_manager.config, f, indent=2)
                print(f"{Colors.GREEN}✅ Enabled {args.enable}{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Unknown provider: {args.enable}{Colors.END}")
        
        elif args.disable:
            if args.disable in sync_manager.config["providers"]:
                sync_manager.config["providers"][args.disable]["enabled"] = False
                with open(sync_manager.config_path, 'w') as f:
                    json.dump(sync_manager.config, f, indent=2)
                print(f"{Colors.YELLOW}⏸️ Disabled {args.disable}{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Unknown provider: {args.disable}{Colors.END}")

if __name__ == "__main__":
    main()