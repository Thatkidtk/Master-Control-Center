#!/usr/bin/env python3
"""
🔍 SMART SEARCH & TAGGING SYSTEM
AI-powered file search with intelligent tagging and content analysis
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import argparse
import mimetypes
import subprocess
import re

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SmartSearch:
    def __init__(self, drive_path="/Volumes/Seagate 2TB"):
        self.drive_path = Path(drive_path)
        self.db_path = self.drive_path / "Scripts" / "search_index.db"
        self.config_path = self.drive_path / "Scripts" / "search_config.json"
        
        self.init_database()
        self.load_config()
    
    def init_database(self):
        """Initialize SQLite database for search index"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                extension TEXT,
                size INTEGER,
                modified INTEGER,
                file_hash TEXT,
                mime_type TEXT,
                content_preview TEXT,
                tags TEXT,
                custom_tags TEXT,
                indexed_date INTEGER,
                project_id TEXT,
                owner TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY,
                query TEXT NOT NULL,
                results_count INTEGER,
                timestamp INTEGER
            )
        ''')
        
        # Create full-text search virtual table
        self.conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
                filename, content_preview, tags, custom_tags, content=files
            )
        ''')
        
        self.conn.commit()
    
    def load_config(self):
        """Load search configuration"""
        default_config = {
            "index_extensions": [
                ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", 
                ".csv", ".pdf", ".doc", ".docx", ".rtf"
            ],
            "exclude_dirs": [
                ".git", "node_modules", "__pycache__", ".DS_Store", 
                "Temp", ".Trash"
            ],
            "max_content_preview": 1000,
            "auto_tag_patterns": {
                "code": [".py", ".js", ".html", ".css", ".json"],
                "document": [".pdf", ".doc", ".docx", ".txt", ".md"],
                "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                "video": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
                "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"]
            },
            "smart_tagging": True
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except json.JSONDecodeError:
                pass
        
        self.config = default_config
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def calculate_file_hash(self, filepath):
        """Calculate file hash for change detection"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return None
    
    def extract_content_preview(self, filepath):
        """Extract content preview from file"""
        try:
            # Text files
            if filepath.suffix.lower() in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(self.config["max_content_preview"])
                    return content.strip()
            
            # PDF files (requires pdftotext)
            elif filepath.suffix.lower() == '.pdf':
                try:
                    result = subprocess.run(
                        ['pdftotext', '-l', '2', str(filepath), '-'],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        return result.stdout[:self.config["max_content_preview"]]
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            # Image EXIF data (requires exiftool)
            elif filepath.suffix.lower() in ['.jpg', '.jpeg', '.tiff']:
                try:
                    result = subprocess.run(
                        ['exiftool', '-s', '-s', '-s', str(filepath)],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        return result.stdout[:500]
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            return ""
        except Exception:
            return ""
    
    def generate_auto_tags(self, filepath, content_preview=""):
        """Generate automatic tags based on file analysis"""
        tags = set()
        
        # Extension-based tags
        ext = filepath.suffix.lower()
        for tag_type, extensions in self.config["auto_tag_patterns"].items():
            if ext in extensions:
                tags.add(tag_type)
        
        # Path-based tags
        path_parts = str(filepath).lower().split('/')
        for part in path_parts:
            if part in ['projects', 'work', 'personal', 'creative', 'learning']:
                tags.add(part)
            if part.startswith('202'):  # Year folders
                tags.add('year_' + part)
        
        # Content-based tags
        if content_preview:
            content_lower = content_preview.lower()
            
            # Programming languages
            if 'def ' in content_lower or 'function ' in content_lower:
                tags.add('programming')
            if 'import ' in content_lower or 'require(' in content_lower:
                tags.add('code')
            
            # Document types
            if any(word in content_lower for word in ['todo', 'task', 'deadline']):
                tags.add('planning')
            if any(word in content_lower for word in ['meeting', 'notes', 'discussion']):
                tags.add('notes')
            if any(word in content_lower for word in ['budget', 'cost', '$', 'expense']):
                tags.add('financial')
        
        # File size tags
        try:
            size_mb = filepath.stat().st_size / (1024 * 1024)
            if size_mb > 100:
                tags.add('large_file')
            elif size_mb < 0.1:
                tags.add('small_file')
        except OSError:
            pass
        
        return list(tags)
    
    def index_file(self, filepath):
        """Index a single file"""
        try:
            stat = filepath.stat()
            file_hash = self.calculate_file_hash(filepath)
            content_preview = self.extract_content_preview(filepath)
            auto_tags = self.generate_auto_tags(filepath, content_preview)
            mime_type, _ = mimetypes.guess_type(str(filepath))
            
            # Check if file changed
            cursor = self.conn.execute(
                'SELECT file_hash FROM files WHERE path = ?', (str(filepath),)
            )
            row = cursor.fetchone()
            
            if row and row[0] == file_hash:
                return False  # File unchanged
            
            # Extract project info from path
            project_id = None
            owner = "Unknown"
            
            if '/Work/' in str(filepath):
                parts = str(filepath).split('/Work/')
                if len(parts) > 1:
                    owner = parts[1].split('/')[0]
            elif '/Personal/' in str(filepath):
                parts = str(filepath).split('/Personal/')
                if len(parts) > 1:
                    owner = parts[1].split('/')[0]
            
            # Insert/update file record
            self.conn.execute('''
                INSERT OR REPLACE INTO files 
                (path, filename, extension, size, modified, file_hash, mime_type, 
                 content_preview, tags, indexed_date, project_id, owner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(filepath),
                filepath.name,
                filepath.suffix.lower(),
                stat.st_size,
                int(stat.st_mtime),
                file_hash,
                mime_type or '',
                content_preview,
                ','.join(auto_tags),
                int(datetime.now().timestamp()),
                project_id,
                owner
            ))
            
            # Update FTS index
            self.conn.execute('''
                INSERT OR REPLACE INTO files_fts 
                (rowid, filename, content_preview, tags, custom_tags)
                SELECT id, filename, content_preview, tags, custom_tags
                FROM files WHERE path = ?
            ''', (str(filepath),))
            
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to index {filepath}: {e}{Colors.END}")
            return False
    
    def build_index(self, force_rebuild=False):
        """Build/rebuild the search index"""
        if force_rebuild:
            self.conn.execute('DELETE FROM files')
            self.conn.execute('DELETE FROM files_fts')
            self.conn.commit()
        
        print(f"{Colors.BLUE}🔍 Building search index...{Colors.END}")
        
        indexed_count = 0
        skipped_count = 0
        
        # Walk through all files
        for root, dirs, files in os.walk(self.drive_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.config["exclude_dirs"]]
            
            root_path = Path(root)
            
            for file in files:
                filepath = root_path / file
                
                # Skip hidden files
                if file.startswith('.'):
                    continue
                
                # Skip files not in index extensions (if specified)
                if (self.config["index_extensions"] and 
                    filepath.suffix.lower() not in self.config["index_extensions"]):
                    continue
                
                if self.index_file(filepath):
                    indexed_count += 1
                else:
                    skipped_count += 1
                
                if (indexed_count + skipped_count) % 100 == 0:
                    print(f"{Colors.YELLOW}📊 Progress: {indexed_count} indexed, {skipped_count} skipped{Colors.END}")
        
        self.conn.commit()
        
        print(f"{Colors.GREEN}✅ Index complete! {indexed_count} files indexed, {skipped_count} unchanged{Colors.END}")
    
    def search(self, query, file_type=None, owner=None, date_range=None, limit=50):
        """Perform intelligent search"""
        # Record search in history
        self.conn.execute(
            'INSERT INTO search_history (query, timestamp) VALUES (?, ?)',
            (query, int(datetime.now().timestamp()))
        )
        
        # Build search query
        sql_parts = []
        params = []
        
        # Full-text search
        if query.strip():
            sql_parts.append('''
                SELECT files.*, 
                       files_fts.rank as relevance
                FROM files_fts 
                JOIN files ON files_fts.rowid = files.id
                WHERE files_fts MATCH ?
            ''')
            # Boost filename matches
            fts_query = f'"{query}" OR filename:{query}*'
            params.append(fts_query)
        else:
            sql_parts.append('SELECT *, 0 as relevance FROM files WHERE 1=1')
        
        # Add filters
        filters = []
        
        if file_type:
            if file_type in self.config["auto_tag_patterns"]:
                extensions = self.config["auto_tag_patterns"][file_type]
                placeholders = ','.join('?' * len(extensions))
                filters.append(f'extension IN ({placeholders})')
                params.extend(extensions)
            else:
                filters.append('tags LIKE ?')
                params.append(f'%{file_type}%')
        
        if owner:
            filters.append('owner = ?')
            params.append(owner)
        
        if date_range:
            if len(date_range) == 2:
                filters.append('modified BETWEEN ? AND ?')
                params.extend(date_range)
        
        if filters:
            if sql_parts[0].startswith('SELECT files.*'):
                sql_parts[0] += ' AND ' + ' AND '.join(filters)
            else:
                sql_parts[0] += ' AND ' + ' AND '.join(filters)
        
        # Add ordering and limit
        if query.strip():
            sql_parts.append('ORDER BY relevance DESC, modified DESC')
        else:
            sql_parts.append('ORDER BY modified DESC')
        
        sql_parts.append(f'LIMIT {limit}')
        
        full_query = ' '.join(sql_parts)
        
        # Execute search
        cursor = self.conn.execute(full_query, params)
        results = cursor.fetchall()
        
        # Update search history with result count
        self.conn.execute(
            'UPDATE search_history SET results_count = ? WHERE rowid = last_insert_rowid()',
            (len(results),)
        )
        self.conn.commit()
        
        return results
    
    def display_results(self, results, show_preview=True):
        """Display search results in a formatted way"""
        if not results:
            print(f"{Colors.YELLOW}📭 No results found{Colors.END}")
            return
        
        print(f"{Colors.BOLD}{Colors.PURPLE}🔍 SEARCH RESULTS ({len(results)} found){Colors.END}")
        print(f"{Colors.BLUE}{'='*80}{Colors.END}")
        
        for i, result in enumerate(results, 1):
            filepath = Path(result[1])  # path column
            size_mb = result[4] / (1024 * 1024) if result[4] else 0  # size column
            modified = datetime.fromtimestamp(result[5]) if result[5] else datetime.now()  # modified column
            tags = result[9] if result[9] else ""  # tags column
            
            print(f"{Colors.BOLD}{i}. {filepath.name}{Colors.END}")
            print(f"   📁 {Colors.CYAN}{filepath.parent}{Colors.END}")
            print(f"   📊 {size_mb:.1f} MB | 📅 {modified.strftime('%Y-%m-%d %H:%M')} | "
                  f"🏷️ {Colors.YELLOW}{tags.replace(',', ', ')}{Colors.END}")
            
            if show_preview and result[8]:  # content_preview column
                preview = result[8][:200].replace('\n', ' ')
                if len(result[8]) > 200:
                    preview += "..."
                print(f"   💬 {Colors.WHITE}{preview}{Colors.END}")
            
            print()
    
    def add_custom_tag(self, filepath, tag):
        """Add custom tag to a file"""
        cursor = self.conn.execute(
            'SELECT custom_tags FROM files WHERE path = ?', (str(filepath),)
        )
        row = cursor.fetchone()
        
        if row:
            current_tags = set(row[0].split(',') if row[0] else [])
            current_tags.add(tag)
            
            self.conn.execute(
                'UPDATE files SET custom_tags = ? WHERE path = ?',
                (','.join(current_tags), str(filepath))
            )
            
            # Update FTS
            self.conn.execute('''
                UPDATE files_fts SET custom_tags = ?
                WHERE rowid = (SELECT id FROM files WHERE path = ?)
            ''', (','.join(current_tags), str(filepath)))
            
            self.conn.commit()
            print(f"{Colors.GREEN}✅ Tag '{tag}' added to {filepath.name}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ File not found in index{Colors.END}")
    
    def get_search_statistics(self):
        """Get search and indexing statistics"""
        cursor = self.conn.execute('SELECT COUNT(*) FROM files')
        total_files = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT COUNT(DISTINCT query) FROM search_history')
        unique_queries = cursor.fetchone()[0]
        
        cursor = self.conn.execute('''
            SELECT query, COUNT(*) as count 
            FROM search_history 
            GROUP BY query 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        top_queries = cursor.fetchall()
        
        print(f"{Colors.BOLD}{Colors.PURPLE}📊 SEARCH STATISTICS{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        print(f"Indexed files: {Colors.YELLOW}{total_files:,}{Colors.END}")
        print(f"Unique searches: {Colors.YELLOW}{unique_queries:,}{Colors.END}")
        
        if top_queries:
            print(f"\n{Colors.BOLD}🔥 Top Search Queries:{Colors.END}")
            for query, count in top_queries:
                print(f"  {Colors.CYAN}'{query}'{Colors.END} - {count} times")

def main():
    parser = argparse.ArgumentParser(description='🔍 Smart Search & Tagging System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Build search index')
    index_parser.add_argument('--rebuild', action='store_true', help='Force rebuild')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search files')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', help='File type filter')
    search_parser.add_argument('--owner', help='Owner filter')
    search_parser.add_argument('--limit', type=int, default=50, help='Result limit')
    search_parser.add_argument('--no-preview', action='store_true', help='Hide content preview')
    
    # Tag command
    tag_parser = subparsers.add_parser('tag', help='Add custom tag')
    tag_parser.add_argument('filepath', help='File path')
    tag_parser.add_argument('tag', help='Tag to add')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    search_engine = SmartSearch()
    
    if args.command == 'index':
        search_engine.build_index(force_rebuild=args.rebuild)
    
    elif args.command == 'search':
        results = search_engine.search(
            args.query, 
            file_type=args.type,
            owner=args.owner,
            limit=args.limit
        )
        search_engine.display_results(results, show_preview=not args.no_preview)
    
    elif args.command == 'tag':
        search_engine.add_custom_tag(Path(args.filepath), args.tag)
    
    elif args.command == 'stats':
        search_engine.get_search_statistics()

if __name__ == "__main__":
    main()