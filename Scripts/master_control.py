#!/usr/bin/env python3
"""
🎛️ MASTER CONTROL CENTER
Unified interface for all 2TB drive systems and automation
"""

import os
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MasterControl:
    def __init__(self, drive_path="/Volumes/Seagate 2TB"):
        self.drive_path = Path(drive_path)
        self.scripts_path = self.drive_path / "Scripts"
        
        # Available systems
        self.systems = {
            "organize": {
                "script": "organize.sh",
                "description": "File organization and cleanup",
                "commands": ["all", "downloads", "cleanup", "report"]
            },
            "backup": {
                "script": "smart_backup.sh", 
                "description": "Intelligent backup system",
                "commands": ["full", "photos", "music", "videos"]
            },
            "media": {
                "script": "media_processor.sh",
                "description": "Advanced media processing",
                "commands": ["photos", "videos", "music", "thumbnails", "all"]
            },
            "duplicates": {
                "script": "duplicate_hunter.py",
                "description": "Intelligent duplicate detection",
                "commands": ["--interactive", "--report duplicates.json"]
            },
            "health": {
                "script": "drive_guardian.py",
                "description": "Drive health monitoring",
                "commands": ["--config"]
            },
            "projects": {
                "script": "project_manager.py",
                "description": "Project lifecycle management", 
                "commands": ["list", "create PROJECT_NAME", "stats --id ID"]
            },
            "search": {
                "script": "smart_search.py",
                "description": "AI-powered file search",
                "commands": ["index", "search QUERY", "stats"]
            },
            "cloud": {
                "script": "cloud_sync.py",
                "description": "Multi-cloud synchronization",
                "commands": ["sync", "status", "daemon"]
            }
        }
    
    def show_banner(self):
        """Display system banner"""
        banner = f"""{Colors.BOLD}{Colors.PURPLE}
╔══════════════════════════════════════════════════════════════╗
║                    🎛️ MASTER CONTROL CENTER                  ║
║                  Ultimate 2TB Drive Management               ║  
╚══════════════════════════════════════════════════════════════╝{Colors.END}
"""
        print(banner)
    
    def show_dashboard(self):
        """Display system dashboard"""
        self.show_banner()
        
        print(f"{Colors.BOLD}{Colors.CYAN}📊 SYSTEM OVERVIEW{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        # Drive stats
        try:
            import psutil
            usage = psutil.disk_usage(str(self.drive_path))
            used_pct = (usage.used / usage.total) * 100
            
            color = Colors.RED if used_pct > 90 else Colors.YELLOW if used_pct > 80 else Colors.GREEN
            print(f"💾 Storage: {color}{usage.used/(1024**3):.1f}GB / {usage.total/(1024**3):.1f}GB ({used_pct:.1f}%){Colors.END}")
            print(f"💿 Free Space: {Colors.GREEN}{usage.free/(1024**3):.1f}GB{Colors.END}")
        except ImportError:
            print(f"{Colors.YELLOW}💾 Storage info requires 'pip install psutil'{Colors.END}")
        
        # File counts by type
        try:
            media_count = len(list(self.drive_path.glob("Media/**/*")))
            work_count = len(list(self.drive_path.glob("Work/**/*")))
            creative_count = len(list(self.drive_path.glob("Creative/**/*")))
            
            print(f"📁 Files: Media({media_count}) | Work({work_count}) | Creative({creative_count})")
        except:
            pass
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 AVAILABLE SYSTEMS{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        for name, system in self.systems.items():
            script_path = self.scripts_path / system["script"]
            status = f"{Colors.GREEN}✓{Colors.END}" if script_path.exists() else f"{Colors.RED}✗{Colors.END}"
            
            print(f"{status} {Colors.BOLD}{name:<12}{Colors.END} - {system['description']}")
            print(f"   {Colors.CYAN}Examples: {' | '.join(system['commands'][:3])}{Colors.END}")
        
        print(f"\n{Colors.BOLD}{Colors.YELLOW}⚡ QUICK COMMANDS{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"  {Colors.GREEN}python3 master_control.py run organize all{Colors.END}")
        print(f"  {Colors.GREEN}python3 master_control.py run backup full{Colors.END}")
        print(f"  {Colors.GREEN}python3 master_control.py run duplicates --interactive{Colors.END}")
        print(f"  {Colors.GREEN}python3 master_control.py run health{Colors.END}")
        print(f"  {Colors.GREEN}python3 master_control.py auto{Colors.END}")
        
        print(f"\n{Colors.CYAN}💡 Type 'python3 master_control.py --help' for full command list{Colors.END}")
    
    def run_system(self, system_name, *args):
        """Run a specific system with arguments"""
        if system_name not in self.systems:
            print(f"{Colors.RED}❌ Unknown system: {system_name}{Colors.END}")
            print(f"Available systems: {', '.join(self.systems.keys())}")
            return False
        
        system = self.systems[system_name]
        script_path = self.scripts_path / system["script"]
        
        if not script_path.exists():
            print(f"{Colors.RED}❌ Script not found: {script_path}{Colors.END}")
            return False
        
        print(f"{Colors.BLUE}🚀 Running {system['description']}...{Colors.END}")
        
        try:
            # Determine if it's a Python or shell script
            if script_path.suffix == '.py':
                cmd = ["python3", str(script_path)] + list(args)
            else:
                cmd = [str(script_path)] + list(args)
            
            result = subprocess.run(cmd, cwd=str(self.drive_path))
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {system['description']} completed successfully{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ {system['description']} failed (exit code: {result.returncode}){Colors.END}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Error running {system_name}: {e}{Colors.END}")
            return False
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Command not found. Make sure all dependencies are installed.{Colors.END}")
            return False
    
    def run_automation_sequence(self):
        """Run automated maintenance sequence"""
        print(f"{Colors.BOLD}{Colors.PURPLE}🤖 RUNNING AUTOMATION SEQUENCE{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        sequences = [
            ("organize", ["all"], "Organizing and cleaning files"),
            ("health", [], "Checking drive health"),
            ("duplicates", ["--scan-only"], "Scanning for duplicates"),
            ("backup", ["full"], "Performing backup"),
        ]
        
        results = []
        
        for system_name, args, description in sequences:
            print(f"\n{Colors.YELLOW}⚡ {description}...{Colors.END}")
            success = self.run_system(system_name, *args)
            results.append((description, success))
        
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📋 AUTOMATION SUMMARY{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        for description, success in results:
            status = f"{Colors.GREEN}✅ SUCCESS{Colors.END}" if success else f"{Colors.RED}❌ FAILED{Colors.END}"
            print(f"{status} {description}")
        
        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        
        if success_count == total_count:
            print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All automation tasks completed successfully!{Colors.END}")
        else:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠️ {success_count}/{total_count} tasks completed{Colors.END}")
    
    def show_system_help(self, system_name):
        """Show help for a specific system"""
        if system_name not in self.systems:
            print(f"{Colors.RED}❌ Unknown system: {system_name}{Colors.END}")
            return
        
        system = self.systems[system_name]
        print(f"{Colors.BOLD}{Colors.PURPLE}{system_name.upper()} - {system['description']}{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"Script: {system['script']}")
        print(f"Common commands:")
        
        for cmd in system['commands']:
            print(f"  {Colors.GREEN}python3 master_control.py run {system_name} {cmd}{Colors.END}")
    
    def create_desktop_shortcuts(self):
        """Create desktop shortcuts for common operations"""
        shortcuts = {
            "Quick Organize": "run organize all",
            "Full Backup": "run backup full", 
            "Health Check": "run health",
            "Find Duplicates": "run duplicates --interactive",
            "System Dashboard": "dashboard"
        }
        
        desktop_path = Path.home() / "Desktop"
        if not desktop_path.exists():
            print(f"{Colors.RED}❌ Desktop folder not found{Colors.END}")
            return
        
        print(f"{Colors.BLUE}🖥️ Creating desktop shortcuts...{Colors.END}")
        
        for name, command in shortcuts.items():
            shortcut_content = f'''#!/bin/bash
# {name} - 2TB Drive System
cd "{self.drive_path}"
python3 "{self.scripts_path}/master_control.py" {command}
read -p "Press Enter to close..."
'''
            
            shortcut_path = desktop_path / f"2TB-{name.replace(' ', '_')}.command"
            
            with open(shortcut_path, 'w') as f:
                f.write(shortcut_content)
            
            # Make executable
            os.chmod(shortcut_path, 0o755)
            
            print(f"{Colors.GREEN}✅ Created: {shortcut_path.name}{Colors.END}")
        
        print(f"{Colors.CYAN}💡 Double-click shortcuts from Desktop to run operations{Colors.END}")

def main():
    parser = argparse.ArgumentParser(
        description='🎛️ Master Control Center for 2TB Drive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 master_control.py dashboard          # Show system dashboard
  python3 master_control.py run organize all  # Run file organization
  python3 master_control.py run backup full   # Perform full backup
  python3 master_control.py auto              # Run automation sequence
  python3 master_control.py help organize     # Show help for organize system
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Dashboard command
    subparsers.add_parser('dashboard', help='Show system dashboard')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a system')
    run_parser.add_argument('system', help='System name')
    run_parser.add_argument('args', nargs='*', help='System arguments')
    
    # Auto command
    subparsers.add_parser('auto', help='Run automation sequence')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show system help')
    help_parser.add_argument('system', help='System name')
    
    # Shortcuts command
    subparsers.add_parser('shortcuts', help='Create desktop shortcuts')
    
    args = parser.parse_args()
    
    control = MasterControl()
    
    if not args.command or args.command == 'dashboard':
        control.show_dashboard()
    
    elif args.command == 'run':
        control.run_system(args.system, *args.args)
    
    elif args.command == 'auto':
        control.run_automation_sequence()
    
    elif args.command == 'help':
        control.show_system_help(args.system)
    
    elif args.command == 'shortcuts':
        control.create_desktop_shortcuts()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()