#!/usr/bin/env python3
"""
🔍 INTELLIGENT DUPLICATE FILE HUNTER
Advanced duplicate detection with AI-powered analysis
"""

import os
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime
import sys

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DuplicateHunter:
    def __init__(self, root_path="/Volumes/Seagate 2TB"):
        self.root_path = Path(root_path)
        self.duplicates = defaultdict(list)
        self.file_hashes = {}
        self.stats = {
            'total_files': 0,
            'duplicate_groups': 0,
            'space_wasted': 0,
            'processed_size': 0
        }
    
    def calculate_hash(self, filepath, chunk_size=8192):
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError):
            return None
    
    def get_file_info(self, filepath):
        """Extract detailed file information"""
        try:
            stat = filepath.stat()
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'path': str(filepath),
                'name': filepath.name,
                'extension': filepath.suffix.lower()
            }
        except (OSError, IOError):
            return None
    
    def scan_directory(self, directory, extensions=None, min_size=0):
        """Scan directory for duplicate files"""
        print(f"{Colors.BLUE}🔍 Scanning: {directory}{Colors.END}")
        
        files_processed = 0
        for filepath in directory.rglob('*'):
            if not filepath.is_file():
                continue
                
            # Skip hidden files and system files
            if filepath.name.startswith('.'):
                continue
                
            # Filter by extensions if specified
            if extensions and filepath.suffix.lower() not in extensions:
                continue
                
            # Skip small files if min_size specified
            try:
                if filepath.stat().st_size < min_size:
                    continue
            except OSError:
                continue
            
            file_hash = self.calculate_hash(filepath)
            if file_hash:
                file_info = self.get_file_info(filepath)
                if file_info:
                    self.file_hashes[file_hash] = self.file_hashes.get(file_hash, [])
                    self.file_hashes[file_hash].append(file_info)
                    files_processed += 1
                    self.stats['total_files'] += 1
                    self.stats['processed_size'] += file_info['size']
                    
                    if files_processed % 100 == 0:
                        print(f"{Colors.YELLOW}📊 Processed: {files_processed} files{Colors.END}")
    
    def find_duplicates(self):
        """Identify duplicate files"""
        print(f"{Colors.PURPLE}🎯 Analyzing for duplicates...{Colors.END}")
        
        for file_hash, files in self.file_hashes.items():
            if len(files) > 1:
                self.duplicates[file_hash] = files
                self.stats['duplicate_groups'] += 1
                
                # Calculate wasted space (keep largest/newest, count others as waste)
                files_sorted = sorted(files, key=lambda x: (x['size'], x['modified']), reverse=True)
                self.stats['space_wasted'] += sum(f['size'] for f in files_sorted[1:])
    
    def generate_report(self, output_file=None):
        """Generate detailed duplicate report"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'statistics': self.stats,
            'duplicate_groups': []
        }
        
        for file_hash, files in self.duplicates.items():
            group = {
                'hash': file_hash,
                'count': len(files),
                'files': files,
                'total_size': sum(f['size'] for f in files),
                'recommendation': self._get_recommendation(files)
            }
            report['duplicate_groups'].append(group)
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        return report
    
    def _get_recommendation(self, files):
        """AI-powered recommendation for which files to keep/delete"""
        # Sort by: newest first, then by path preference
        priority_paths = ['Edited', 'Final', 'Best', 'Projects']
        
        def path_score(file_info):
            path = file_info['path'].lower()
            score = 0
            
            # Prefer files in certain directories
            for priority in priority_paths:
                if priority.lower() in path:
                    score += 10
            
            # Prefer files not in temp/downloads
            if 'temp' in path or 'download' in path:
                score -= 5
            
            # Prefer newer files
            score += hash(file_info['modified']) % 3
            
            return score
        
        sorted_files = sorted(files, key=path_score, reverse=True)
        
        return {
            'keep': sorted_files[0]['path'],
            'delete': [f['path'] for f in sorted_files[1:]]
        }
    
    def interactive_cleanup(self):
        """Interactive duplicate cleanup"""
        print(f"{Colors.BOLD}{Colors.GREEN}🧹 INTERACTIVE CLEANUP MODE{Colors.END}")
        print(f"{Colors.YELLOW}Found {len(self.duplicates)} duplicate groups{Colors.END}")
        
        deleted_count = 0
        space_freed = 0
        
        for file_hash, files in self.duplicates.items():
            print(f"\n{Colors.CYAN}📁 Duplicate Group ({len(files)} files):{Colors.END}")
            
            for i, file_info in enumerate(files, 1):
                size_mb = file_info['size'] / (1024 * 1024)
                print(f"  {i}. {file_info['path']} ({size_mb:.1f} MB)")
            
            recommendation = self._get_recommendation(files)
            print(f"{Colors.GREEN}💡 Recommended: Keep {recommendation['keep']}{Colors.END}")
            
            choice = input(f"{Colors.YELLOW}Action: (a)uto-delete recommended, (s)kip, (q)uit: {Colors.END}").lower()
            
            if choice == 'q':
                break
            elif choice == 'a':
                for delete_path in recommendation['delete']:
                    try:
                        file_size = Path(delete_path).stat().st_size
                        os.remove(delete_path)
                        deleted_count += 1
                        space_freed += file_size
                        print(f"{Colors.RED}🗑️  Deleted: {delete_path}{Colors.END}")
                    except OSError as e:
                        print(f"{Colors.RED}❌ Failed to delete {delete_path}: {e}{Colors.END}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Cleanup Complete!{Colors.END}")
        print(f"Deleted: {deleted_count} files")
        print(f"Space freed: {space_freed / (1024*1024*1024):.2f} GB")
    
    def print_summary(self):
        """Print scan summary"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📊 DUPLICATE SCAN SUMMARY{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        print(f"Total files scanned: {Colors.YELLOW}{self.stats['total_files']:,}{Colors.END}")
        print(f"Duplicate groups found: {Colors.YELLOW}{self.stats['duplicate_groups']:,}{Colors.END}")
        print(f"Space wasted by duplicates: {Colors.RED}{self.stats['space_wasted']/(1024*1024*1024):.2f} GB{Colors.END}")
        print(f"Total data processed: {Colors.GREEN}{self.stats['processed_size']/(1024*1024*1024):.2f} GB{Colors.END}")

def main():
    parser = argparse.ArgumentParser(description='🔍 Intelligent Duplicate File Hunter')
    parser.add_argument('--path', default='/Volumes/Seagate 2TB', help='Root path to scan')
    parser.add_argument('--extensions', nargs='+', help='File extensions to scan (e.g., .jpg .mp4)')
    parser.add_argument('--min-size', type=int, default=1024*1024, help='Minimum file size in bytes (default: 1MB)')
    parser.add_argument('--report', help='Output report to JSON file')
    parser.add_argument('--interactive', action='store_true', help='Interactive cleanup mode')
    parser.add_argument('--scan-only', action='store_true', help='Scan only, no cleanup')
    
    args = parser.parse_args()
    
    if not Path(args.path).exists():
        print(f"{Colors.RED}❌ Path not found: {args.path}{Colors.END}")
        sys.exit(1)
    
    hunter = DuplicateHunter(args.path)
    
    # Scan for duplicates
    hunter.scan_directory(
        Path(args.path),
        extensions=args.extensions,
        min_size=args.min_size
    )
    
    # Find duplicates
    hunter.find_duplicates()
    
    # Print summary
    hunter.print_summary()
    
    # Generate report if requested
    if args.report:
        hunter.generate_report(args.report)
        print(f"{Colors.GREEN}📄 Report saved to: {args.report}{Colors.END}")
    
    # Interactive cleanup if requested
    if args.interactive and not args.scan_only:
        hunter.interactive_cleanup()

if __name__ == "__main__":
    main()