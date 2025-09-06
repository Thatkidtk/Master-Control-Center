#!/usr/bin/env python3
"""
🛡️ DRIVE GUARDIAN - Advanced Health Monitoring System
Real-time drive health monitoring with intelligent alerts
"""

import os
import json
import subprocess
import psutil
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DriveGuardian:
    def __init__(self, drive_path="/Volumes/Seagate 2TB"):
        self.drive_path = Path(drive_path)
        self.config_file = self.drive_path / ".guardian_config.json"
        self.log_file = self.drive_path / "Scripts" / "guardian.log"
        self.health_data = self.drive_path / "Scripts" / "health_history.json"
        
        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.config = self.load_config()
        self.health_history = self.load_health_history()
    
    def load_config(self):
        """Load configuration settings"""
        default_config = {
            "alerts": {
                "space_warning_percent": 85,
                "space_critical_percent": 95,
                "temp_files_warning_gb": 10,
                "old_files_warning_days": 365
            },
            "notifications": {
                "email_enabled": False,
                "email": "your-email@example.com",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587
            },
            "monitoring": {
                "check_interval_hours": 24,
                "keep_history_days": 90
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key in loaded_config:
                        default_config[key].update(loaded_config[key])
                return default_config
            except json.JSONDecodeError:
                pass
        
        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def load_health_history(self):
        """Load health monitoring history"""
        if self.health_data.exists():
            try:
                with open(self.health_data, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"entries": []}
    
    def save_health_history(self):
        """Save health history to file"""
        with open(self.health_data, 'w') as f:
            json.dump(self.health_history, f, indent=2)
    
    def get_disk_usage(self):
        """Get disk usage statistics"""
        try:
            usage = psutil.disk_usage(str(self.drive_path))
            return {
                "total_gb": usage.total / (1024**3),
                "used_gb": usage.used / (1024**3),
                "free_gb": usage.free / (1024**3),
                "used_percent": (usage.used / usage.total) * 100
            }
        except Exception as e:
            logging.error(f"Failed to get disk usage: {e}")
            return None
    
    def get_smart_data(self):
        """Get SMART data from drive (requires smartctl)"""
        try:
            # Find the actual disk device
            result = subprocess.run(
                ["diskutil", "info", str(self.drive_path)],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                device_node = None
                for line in lines:
                    if 'Device Node:' in line:
                        device_node = line.split(':')[1].strip()
                        break
                
                if device_node:
                    # Get SMART data
                    smart_result = subprocess.run(
                        ["smartctl", "-a", device_node],
                        capture_output=True, text=True
                    )
                    
                    if smart_result.returncode in [0, 64]:  # 64 is OK for some drives
                        return {"available": True, "raw_output": smart_result.stdout}
            
            return {"available": False, "error": "SMART data not accessible"}
        except FileNotFoundError:
            return {"available": False, "error": "smartctl not installed"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def analyze_folder_sizes(self):
        """Analyze folder sizes and identify large directories"""
        folder_sizes = {}
        
        try:
            for item in self.drive_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        # Use du command for accurate size calculation
                        result = subprocess.run(
                            ["du", "-sh", str(item)],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            size_str = result.stdout.split('\t')[0].strip()
                            folder_sizes[item.name] = size_str
                    except Exception:
                        pass
            
            return folder_sizes
        except Exception as e:
            logging.error(f"Failed to analyze folder sizes: {e}")
            return {}
    
    def find_large_files(self, size_mb=100, limit=20):
        """Find large files on the drive"""
        large_files = []
        
        try:
            # Use find command to locate large files
            size_bytes = size_mb * 1024 * 1024
            result = subprocess.run([
                "find", str(self.drive_path), "-type", "f", "-size", f"+{size_bytes}c",
                "-exec", "ls", "-lh", "{}", ";"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[:limit]:
                    if line:
                        parts = line.split()
                        if len(parts) >= 9:
                            size = parts[4]
                            filename = ' '.join(parts[8:])
                            large_files.append({"size": size, "path": filename})
            
            return large_files
        except Exception as e:
            logging.error(f"Failed to find large files: {e}")
            return []
    
    def check_temp_files(self):
        """Check for excessive temporary files"""
        temp_paths = [
            self.drive_path / "Temp",
            self.drive_path / "Downloads",
            self.drive_path / ".Trash"
        ]
        
        temp_stats = {}
        total_temp_size = 0
        
        for temp_path in temp_paths:
            if temp_path.exists():
                try:
                    result = subprocess.run(
                        ["du", "-sh", str(temp_path)],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        size_str = result.stdout.split('\t')[0].strip()
                        temp_stats[temp_path.name] = size_str
                        
                        # Convert to GB for total calculation
                        if 'G' in size_str:
                            total_temp_size += float(size_str.replace('G', ''))
                        elif 'M' in size_str:
                            total_temp_size += float(size_str.replace('M', '')) / 1024
                except Exception:
                    pass
        
        return {
            "folders": temp_stats,
            "total_gb": total_temp_size
        }
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "disk_usage": self.get_disk_usage(),
            "smart_data": self.get_smart_data(),
            "folder_sizes": self.analyze_folder_sizes(),
            "large_files": self.find_large_files(),
            "temp_files": self.check_temp_files(),
            "alerts": []
        }
        
        # Check for alerts
        if report["disk_usage"]:
            usage_percent = report["disk_usage"]["used_percent"]
            if usage_percent > self.config["alerts"]["space_critical_percent"]:
                report["alerts"].append({
                    "level": "CRITICAL",
                    "message": f"Disk usage is {usage_percent:.1f}% - critically high!"
                })
            elif usage_percent > self.config["alerts"]["space_warning_percent"]:
                report["alerts"].append({
                    "level": "WARNING",
                    "message": f"Disk usage is {usage_percent:.1f}% - approaching limit"
                })
        
        if report["temp_files"]["total_gb"] > self.config["alerts"]["temp_files_warning_gb"]:
            report["alerts"].append({
                "level": "WARNING",
                "message": f"Temporary files using {report['temp_files']['total_gb']:.1f} GB"
            })
        
        return report
    
    def print_health_report(self, report):
        """Print formatted health report"""
        print(f"{Colors.BOLD}{Colors.PURPLE}🛡️ DRIVE GUARDIAN HEALTH REPORT{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"Scan Time: {Colors.CYAN}{report['timestamp']}{Colors.END}\n")
        
        # Disk Usage
        if report["disk_usage"]:
            usage = report["disk_usage"]
            color = Colors.RED if usage["used_percent"] > 90 else Colors.YELLOW if usage["used_percent"] > 80 else Colors.GREEN
            print(f"{Colors.BOLD}💾 Disk Usage:{Colors.END}")
            print(f"  Total: {usage['total_gb']:.1f} GB")
            print(f"  Used: {color}{usage['used_gb']:.1f} GB ({usage['used_percent']:.1f}%){Colors.END}")
            print(f"  Free: {Colors.GREEN}{usage['free_gb']:.1f} GB{Colors.END}\n")
        
        # Alerts
        if report["alerts"]:
            print(f"{Colors.BOLD}{Colors.RED}🚨 ALERTS:{Colors.END}")
            for alert in report["alerts"]:
                color = Colors.RED if alert["level"] == "CRITICAL" else Colors.YELLOW
                print(f"  {color}{alert['level']}: {alert['message']}{Colors.END}")
            print()
        
        # Folder Sizes
        if report["folder_sizes"]:
            print(f"{Colors.BOLD}📁 Top Folders by Size:{Colors.END}")
            for folder, size in list(report["folder_sizes"].items())[:10]:
                print(f"  {folder}: {Colors.CYAN}{size}{Colors.END}")
            print()
        
        # Large Files
        if report["large_files"]:
            print(f"{Colors.BOLD}📄 Large Files (>100MB):{Colors.END}")
            for file_info in report["large_files"][:10]:
                filename = Path(file_info["path"]).name
                print(f"  {Colors.YELLOW}{file_info['size']:<8}{Colors.END} {filename}")
            print()
        
        # Temp Files
        temp = report["temp_files"]
        if temp["total_gb"] > 1:
            color = Colors.RED if temp["total_gb"] > 10 else Colors.YELLOW
            print(f"{Colors.BOLD}🗑️ Temporary Files:{Colors.END}")
            print(f"  Total: {color}{temp['total_gb']:.1f} GB{Colors.END}")
            for folder, size in temp["folders"].items():
                print(f"    {folder}: {size}")
            print()
    
    def cleanup_recommendations(self, report):
        """Generate cleanup recommendations"""
        recommendations = []
        
        if report["temp_files"]["total_gb"] > 5:
            recommendations.append("🧹 Clean temporary files and downloads")
        
        if report["large_files"]:
            recommendations.append("📦 Consider archiving or compressing large files")
        
        if report["disk_usage"] and report["disk_usage"]["used_percent"] > 85:
            recommendations.append("💾 Free up disk space - drive is getting full")
        
        if recommendations:
            print(f"{Colors.BOLD}{Colors.GREEN}💡 CLEANUP RECOMMENDATIONS:{Colors.END}")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
            print()
    
    def monitor(self):
        """Main monitoring function"""
        print(f"{Colors.BLUE}🛡️ Starting Drive Guardian monitoring...{Colors.END}")
        
        report = self.generate_health_report()
        
        # Save to history
        self.health_history["entries"].append(report)
        
        # Keep only recent entries
        cutoff_date = datetime.now() - timedelta(days=self.config["monitoring"]["keep_history_days"])
        self.health_history["entries"] = [
            entry for entry in self.health_history["entries"]
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
        ]
        
        self.save_health_history()
        
        # Print report
        self.print_health_report(report)
        self.cleanup_recommendations(report)
        
        # Log alerts
        for alert in report["alerts"]:
            logging.warning(f"{alert['level']}: {alert['message']}")
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='🛡️ Drive Guardian - Health Monitoring')
    parser.add_argument('--path', default='/Volumes/Seagate 2TB', help='Drive path to monitor')
    parser.add_argument('--config', action='store_true', help='Show configuration')
    
    args = parser.parse_args()
    
    guardian = DriveGuardian(args.path)
    
    if args.config:
        print(f"{Colors.BLUE}📋 Current Configuration:{Colors.END}")
        print(json.dumps(guardian.config, indent=2))
    else:
        guardian.monitor()

if __name__ == "__main__":
    main()