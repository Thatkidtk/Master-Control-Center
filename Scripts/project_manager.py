#!/usr/bin/env python3
"""
🎯 PROJECT LIFECYCLE MANAGER
Advanced project creation, tracking, and management system
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import argparse
import subprocess

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ProjectManager:
    def __init__(self, drive_path="/Volumes/Seagate 2TB"):
        self.drive_path = Path(drive_path)
        self.projects_db = self.drive_path / "Scripts" / "projects.json"
        self.templates_path = self.drive_path / "Templates"
        self.work_path = self.drive_path / "Work"
        self.creative_path = self.drive_path / "Creative"
        
        self.projects = self.load_projects()
    
    def load_projects(self):
        """Load projects database"""
        if self.projects_db.exists():
            try:
                with open(self.projects_db, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"projects": []}
    
    def save_projects(self):
        """Save projects database"""
        with open(self.projects_db, 'w') as f:
            json.dump(self.projects, f, indent=2, default=str)
    
    def create_project(self, name, project_type, owner="You", description="", deadline=None):
        """Create a new project with full structure"""
        project_id = str(uuid.uuid4())[:8]
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        folder_name = f"{safe_name.replace(' ', '-')}-{project_id}"
        
        # Determine project path based on type
        if project_type in ["art", "design", "music", "video", "writing"]:
            base_path = self.creative_path / project_type.title()
        else:
            base_path = self.work_path / owner
        
        project_path = base_path / folder_name
        
        # Create project structure
        project_structure = [
            "01-Planning",
            "02-Resources", 
            "03-Assets",
            "04-Working-Files",
            "05-Reviews",
            "06-Final-Output",
            "99-Archive"
        ]
        
        project_path.mkdir(parents=True, exist_ok=True)
        
        for folder in project_structure:
            (project_path / folder).mkdir(exist_ok=True)
        
        # Create project files
        self._create_project_readme(project_path, name, description, owner)
        self._create_project_config(project_path, project_id, name, project_type)
        self._create_project_log(project_path)
        
        # Add to database
        project_data = {
            "id": project_id,
            "name": name,
            "type": project_type,
            "owner": owner,
            "description": description,
            "path": str(project_path),
            "created": datetime.now().isoformat(),
            "deadline": deadline,
            "status": "planning",
            "progress": 0,
            "last_activity": datetime.now().isoformat(),
            "tasks": [],
            "files_count": 0,
            "total_size_mb": 0
        }
        
        self.projects["projects"].append(project_data)
        self.save_projects()
        
        print(f"{Colors.GREEN}✅ Project '{name}' created successfully!{Colors.END}")
        print(f"{Colors.BLUE}📁 Location: {project_path}{Colors.END}")
        print(f"{Colors.CYAN}🆔 Project ID: {project_id}{Colors.END}")
        
        return project_data
    
    def _create_project_readme(self, project_path, name, description, owner):
        """Create project README file"""
        readme_content = f"""# {name}

**Project Owner**: {owner}  
**Created**: {datetime.now().strftime('%Y-%m-%d')}  
**Status**: 🔄 Planning  

## Description
{description if description else 'Project description goes here...'}

## Project Structure
```
{project_path.name}/
├── 01-Planning/        # Requirements, specs, wireframes
├── 02-Resources/       # Reference materials, links, docs
├── 03-Assets/          # Images, videos, audio files
├── 04-Working-Files/   # Current work in progress
├── 05-Reviews/         # Feedback, versions for review
├── 06-Final-Output/    # Completed deliverables
└── 99-Archive/         # Old versions, unused files
```

## Timeline
- **Planning Phase**: {datetime.now().strftime('%Y-%m-%d')}
- **Development**: TBD
- **Review**: TBD
- **Completion**: TBD

## Notes
Update this file with progress, decisions, and important information.

## Quick Commands
```bash
# Navigate to project
cd "{project_path}"

# Project status
python3 "/Volumes/Seagate 2TB/Scripts/project_manager.py" status --id {project_path.name.split('-')[-1]}

# Update progress
python3 "/Volumes/Seagate 2TB/Scripts/project_manager.py" update --id {project_path.name.split('-')[-1]} --progress 50
```

---
*Generated by Project Manager*
"""
        
        with open(project_path / "README.md", 'w') as f:
            f.write(readme_content)
    
    def _create_project_config(self, project_path, project_id, name, project_type):
        """Create project configuration file"""
        config = {
            "project_id": project_id,
            "name": name,
            "type": project_type,
            "auto_backup": True,
            "compress_archives": True,
            "file_patterns": {
                "ignore": [".DS_Store", "*.tmp", "*.temp", "node_modules"],
                "important": ["*.md", "*.txt", "*.pdf"]
            },
            "integrations": {
                "git_enabled": False,
                "cloud_sync": False
            }
        }
        
        with open(project_path / ".project_config.json", 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_project_log(self, project_path):
        """Create project activity log"""
        log_content = f"# Project Activity Log\n\n{datetime.now().strftime('%Y-%m-%d %H:%M')} - Project created\n"
        
        with open(project_path / "01-Planning" / "project_log.md", 'w') as f:
            f.write(log_content)
    
    def list_projects(self, status_filter=None, owner_filter=None):
        """List all projects with optional filters"""
        projects = self.projects["projects"]
        
        if status_filter:
            projects = [p for p in projects if p["status"] == status_filter]
        
        if owner_filter:
            projects = [p for p in projects if p["owner"] == owner_filter]
        
        if not projects:
            print(f"{Colors.YELLOW}📋 No projects found{Colors.END}")
            return
        
        print(f"{Colors.BOLD}{Colors.PURPLE}📋 PROJECT DASHBOARD{Colors.END}")
        print(f"{Colors.BLUE}{'='*80}{Colors.END}")
        
        # Sort by last activity
        projects.sort(key=lambda x: x["last_activity"], reverse=True)
        
        for project in projects:
            status_color = self._get_status_color(project["status"])
            age_days = (datetime.now() - datetime.fromisoformat(project["created"])).days
            
            print(f"{Colors.BOLD}{project['name']}{Colors.END} {Colors.CYAN}(#{project['id']}){Colors.END}")
            print(f"  Status: {status_color}{project['status'].title()}{Colors.END} | "
                  f"Owner: {Colors.YELLOW}{project['owner']}{Colors.END} | "
                  f"Age: {age_days} days")
            print(f"  Progress: {self._progress_bar(project['progress'])} {project['progress']}%")
            if project.get('deadline'):
                deadline = datetime.fromisoformat(project['deadline'])
                days_left = (deadline - datetime.now()).days
                deadline_color = Colors.RED if days_left < 0 else Colors.YELLOW if days_left < 7 else Colors.GREEN
                print(f"  Deadline: {deadline_color}{deadline.strftime('%Y-%m-%d')} ({days_left} days){Colors.END}")
            print()
    
    def _get_status_color(self, status):
        """Get color for project status"""
        colors = {
            "planning": Colors.BLUE,
            "active": Colors.GREEN,
            "review": Colors.YELLOW,
            "completed": Colors.PURPLE,
            "paused": Colors.CYAN,
            "cancelled": Colors.RED
        }
        return colors.get(status, Colors.WHITE)
    
    def _progress_bar(self, progress, width=20):
        """Generate progress bar"""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        color = Colors.RED if progress < 25 else Colors.YELLOW if progress < 75 else Colors.GREEN
        return f"{color}[{bar}]{Colors.END}"
    
    def update_project(self, project_id, **updates):
        """Update project information"""
        for project in self.projects["projects"]:
            if project["id"] == project_id:
                project.update(updates)
                project["last_activity"] = datetime.now().isoformat()
                self.save_projects()
                print(f"{Colors.GREEN}✅ Project updated successfully{Colors.END}")
                return project
        
        print(f"{Colors.RED}❌ Project not found: {project_id}{Colors.END}")
        return None
    
    def project_stats(self, project_id):
        """Get detailed project statistics"""
        for project in self.projects["projects"]:
            if project["id"] == project_id:
                project_path = Path(project["path"])
                
                if not project_path.exists():
                    print(f"{Colors.RED}❌ Project path not found: {project_path}{Colors.END}")
                    return
                
                # Calculate current stats
                file_count = 0
                total_size = 0
                
                for root, dirs, files in os.walk(project_path):
                    file_count += len(files)
                    for file in files:
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            pass
                
                # Update project data
                project["files_count"] = file_count
                project["total_size_mb"] = total_size / (1024 * 1024)
                self.save_projects()
                
                # Display stats
                print(f"{Colors.BOLD}{Colors.PURPLE}📊 PROJECT STATISTICS{Colors.END}")
                print(f"{Colors.BLUE}{'='*50}{Colors.END}")
                print(f"Name: {Colors.BOLD}{project['name']}{Colors.END}")
                print(f"ID: {Colors.CYAN}{project['id']}{Colors.END}")
                print(f"Status: {self._get_status_color(project['status'])}{project['status'].title()}{Colors.END}")
                print(f"Progress: {self._progress_bar(project['progress'])} {project['progress']}%")
                print(f"Files: {Colors.YELLOW}{file_count:,}{Colors.END}")
                print(f"Size: {Colors.YELLOW}{total_size/(1024*1024):.1f} MB{Colors.END}")
                print(f"Created: {Colors.CYAN}{datetime.fromisoformat(project['created']).strftime('%Y-%m-%d %H:%M')}{Colors.END}")
                print(f"Last Activity: {Colors.CYAN}{datetime.fromisoformat(project['last_activity']).strftime('%Y-%m-%d %H:%M')}{Colors.END}")
                print(f"Path: {Colors.BLUE}{project_path}{Colors.END}")
                
                return project
        
        print(f"{Colors.RED}❌ Project not found: {project_id}{Colors.END}")
    
    def archive_project(self, project_id):
        """Archive completed project"""
        for project in self.projects["projects"]:
            if project["id"] == project_id:
                project_path = Path(project["path"])
                archive_path = self.drive_path / "Archive" / "Projects" / f"{project['name']}-{project_id}.tar.gz"
                
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create compressed archive
                try:
                    subprocess.run([
                        "tar", "-czf", str(archive_path), "-C", str(project_path.parent), project_path.name
                    ], check=True)
                    
                    # Update project status
                    project["status"] = "archived"
                    project["archive_path"] = str(archive_path)
                    project["archived_date"] = datetime.now().isoformat()
                    
                    self.save_projects()
                    
                    print(f"{Colors.GREEN}✅ Project archived successfully{Colors.END}")
                    print(f"{Colors.BLUE}📦 Archive: {archive_path}{Colors.END}")
                    
                    # Ask if user wants to remove original
                    response = input(f"{Colors.YELLOW}Remove original project folder? (y/N): {Colors.END}")
                    if response.lower() == 'y':
                        shutil.rmtree(project_path)
                        print(f"{Colors.GREEN}✅ Original folder removed{Colors.END}")
                    
                    return True
                    
                except subprocess.CalledProcessError as e:
                    print(f"{Colors.RED}❌ Archive failed: {e}{Colors.END}")
                    return False
        
        print(f"{Colors.RED}❌ Project not found: {project_id}{Colors.END}")
        return False

def main():
    parser = argparse.ArgumentParser(description='🎯 Project Lifecycle Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create project
    create_parser = subparsers.add_parser('create', help='Create new project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('--type', default='general', help='Project type')
    create_parser.add_argument('--owner', default='You', help='Project owner')
    create_parser.add_argument('--description', help='Project description')
    create_parser.add_argument('--deadline', help='Project deadline (YYYY-MM-DD)')
    
    # List projects
    list_parser = subparsers.add_parser('list', help='List all projects')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--owner', help='Filter by owner')
    
    # Update project
    update_parser = subparsers.add_parser('update', help='Update project')
    update_parser.add_argument('--id', required=True, help='Project ID')
    update_parser.add_argument('--status', help='New status')
    update_parser.add_argument('--progress', type=int, help='Progress percentage')
    update_parser.add_argument('--deadline', help='New deadline')
    
    # Project stats
    stats_parser = subparsers.add_parser('stats', help='Show project statistics')
    stats_parser.add_argument('--id', required=True, help='Project ID')
    
    # Archive project
    archive_parser = subparsers.add_parser('archive', help='Archive project')
    archive_parser.add_argument('--id', required=True, help='Project ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = ProjectManager()
    
    if args.command == 'create':
        deadline = None
        if args.deadline:
            try:
                deadline = datetime.strptime(args.deadline, '%Y-%m-%d').isoformat()
            except ValueError:
                print(f"{Colors.RED}❌ Invalid deadline format. Use YYYY-MM-DD{Colors.END}")
                return
        
        manager.create_project(
            args.name, args.type, args.owner, 
            args.description or "", deadline
        )
    
    elif args.command == 'list':
        manager.list_projects(args.status, args.owner)
    
    elif args.command == 'update':
        updates = {}
        if args.status:
            updates['status'] = args.status
        if args.progress is not None:
            updates['progress'] = max(0, min(100, args.progress))
        if args.deadline:
            try:
                updates['deadline'] = datetime.strptime(args.deadline, '%Y-%m-%d').isoformat()
            except ValueError:
                print(f"{Colors.RED}❌ Invalid deadline format{Colors.END}")
                return
        
        manager.update_project(args.id, **updates)
    
    elif args.command == 'stats':
        manager.project_stats(args.id)
    
    elif args.command == 'archive':
        manager.archive_project(args.id)

if __name__ == "__main__":
    main()