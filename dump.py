import os
import sys
from typing import List, Set, Optional
import fnmatch

def parse_exclusion_file(file_path: str) -> Set[str]:
    patterns = set()
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.add(line)
    return patterns

def is_excluded(path: str, exclusion_patterns: Set[str]) -> bool:
    for pattern in exclusion_patterns:
        if pattern.startswith('/') and pattern.endswith('/'):
            if path.startswith(pattern[1:]) or path == pattern[1:-1]:
                return True
        elif pattern.endswith('/'):
            if path.startswith(pattern) or path == pattern[:-1]:
                return True
        elif pattern.startswith('/'):
            if path == pattern[1:] or path.startswith(pattern[1:] + os.sep):
                return True
        else:
            if fnmatch.fnmatch(path, pattern) or any(fnmatch.fnmatch(part, pattern) for part in path.split(os.sep)):
                return True
    return False

def print_directory_structure(start_path: str, exclusion_patterns: Set[str]) -> str:
    def _generate_tree(dir_path: str, prefix: str = '') -> List[str]:
        entries = os.listdir(dir_path)
        entries = sorted(entries, key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))
        tree = []
        for i, entry in enumerate(entries):
            rel_path = os.path.relpath(os.path.join(dir_path, entry), start_path)
            if is_excluded(rel_path, exclusion_patterns):
                continue
            
            if i == len(entries) - 1:
                connector = '└── '
                new_prefix = prefix + '    '
            else:
                connector = '├── '
                new_prefix = prefix + '│   '
            
            full_path = os.path.join(dir_path, entry)
            if os.path.isdir(full_path):
                tree.append(f"{prefix}{connector}{entry}/")
                tree.extend(_generate_tree(full_path, new_prefix))
            else:
                tree.append(f"{prefix}{connector}{entry}")
        return tree

    tree = ['/ '] + _generate_tree(start_path)
    return '\n'.join(tree)

def scan_folder(start_path: str, file_types: Optional[List[str]], output_file: str, exclusion_patterns: Set[str]) -> None:
    with open(output_file, 'w', encoding='utf-8') as out_file:
        # Write the directory structure
        out_file.write("Directory Structure:\n")
        out_file.write("-------------------\n")
        out_file.write(print_directory_structure(start_path, exclusion_patterns))
        out_file.write("\n\n")
        out_file.write("File Contents:\n")
        out_file.write("--------------\n")

        for root, dirs, files in os.walk(start_path):
            rel_path = os.path.relpath(root, start_path)
            
            if is_excluded(rel_path, exclusion_patterns):
                continue
            
            for file in files:
                file_rel_path = os.path.join(rel_path, file)
                if is_excluded(file_rel_path, exclusion_patterns):
                    continue
                if file_types is None or any(file.endswith(ext) for ext in file_types):
                    file_path = os.path.join(root, file)
                    
                    print(f"Processing: {file_rel_path}")
                    out_file.write(f"File: {file_rel_path}\n")
                    out_file.write("-" * 50 + "\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as in_file:
                            content = in_file.read()
                            out_file.write(f"Content of {file_rel_path}:\n")
                            out_file.write(content)
                    except Exception as e:
                        print(f"Error reading file {file_rel_path}: {str(e)}. Skipping.")
                        out_file.write(f"Error reading file: {str(e)}. Content skipped.\n")
                    
                    out_file.write("\n\n")

def main(args: List[str]) -> None:
    if len(args) < 3:
        print("Usage: python script.py <start_path> <output_file> [exclusion_file] [file_extensions...]")
        print("Both exclusion_file and file_extensions are optional.")
        sys.exit(1)

    start_path: str = args[1]
    output_file: str = args[2]
    exclusion_file: Optional[str] = None
    file_types: Optional[List[str]] = None

    if len(args) > 3:
        if not args[3].startswith('.'):
            exclusion_file = args[3]
            file_types = args[4:] if len(args) > 4 else None
        else:
            file_types = args[3:]

    exclusion_patterns = parse_exclusion_file(exclusion_file) if exclusion_file else set()
    
    if exclusion_file:
        print(f"Using exclusion patterns from {exclusion_file}: {exclusion_patterns}")
    else:
        print("No exclusion file specified. Scanning all files.")

    if file_types:
        print(f"Scanning for file types: {file_types}")
    else:
        print("No file types specified. Scanning all files.")

    scan_folder(start_path, file_types, output_file, exclusion_patterns)
    print(f"Scan complete. Results written to {output_file}")

if __name__ == "__main__":
    main(sys.argv)