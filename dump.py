


from typing import List, Set, Optional
import fnmatch
import logging
import os
import sys

# Setup logging with DEBUG level for detailed development insights
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Default headers for output file, can be modified for flexibility
DEFAULT_DIRECTORY_HEADER = "Directory Structure:\n-------------------\n"
DEFAULT_FILE_HEADER = "File Contents:\n--------------\n"

def parse_exclusion_file(file_path: str) -> Set[str]:
    """
    Parse the exclusion file to get a set of exclusion patterns.
    Args:
        file_path (str): Path to the exclusion file.
    Returns:
        Set[str]: A set of exclusion patterns.
    """
    patterns = set()
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except IOError as e:
            logging.error(f"Error reading exclusion file {file_path}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while reading {file_path}: {e}")
    return patterns

def is_excluded(path: str, exclusion_patterns: Set[str]) -> bool:
    """
    Check if the file or directory matches any exclusion pattern.
    Args:
        path (str): The file or directory path.
        exclusion_patterns (Set[str]): The set of exclusion patterns.
    Returns:
        bool: True if the path is excluded based on the patterns.
    """
    for pattern in exclusion_patterns:
        try:
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
        except Exception as e:
            logging.error(f"Error processing exclusion pattern {pattern}: {e}")
    return False

def print_directory_structure(start_path: str, exclusion_patterns: Set[str]) -> str:
    """
    Print the directory structure excluding the paths that match exclusion patterns.
    Args:
        start_path (str): The root directory to start scanning.
        exclusion_patterns (Set[str]): The set of exclusion patterns.
    Returns:
        str: A string representation of the directory structure.
    """
    def _generate_tree(dir_path: str, prefix: str = '') -> List[str]:
        entries = os.listdir(dir_path)
        entries = sorted(entries, key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))
        tree = []
        for i, entry in enumerate(entries):
            rel_path = os.path.relpath(os.path.join(dir_path, entry), start_path)
            if is_excluded(rel_path, exclusion_patterns):
                continue

            connector = '└── ' if i == len(entries) - 1 else '├── '
            new_prefix = prefix + ('    ' if i == len(entries) - 1 else '│   ')
            
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
    """
    Scan the folder, write directory structure, and content of files to the output file.
    Args:
        start_path (str): The root directory to start scanning.
        file_types (Optional[List[str]]): List of file extensions to include, or None for all files.
        output_file (str): The file to output the scan results.
        exclusion_patterns (Set[str]): The set of exclusion patterns.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            # Write the directory structure
            out_file.write(DEFAULT_DIRECTORY_HEADER)
            out_file.write(print_directory_structure(start_path, exclusion_patterns))
            out_file.write("\n\n")
            out_file.write(DEFAULT_FILE_HEADER)

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

                        logging.debug(f"Processing: {file_rel_path}")
                        out_file.write(f"File: {file_rel_path}\n")
                        out_file.write("-" * 50 + "\n")

                        try:
                            with open(file_path, 'r', encoding='utf-8') as in_file:
                                content = in_file.read()
                                out_file.write(f"Content of {file_rel_path}:\n")
                                out_file.write(content)
                        except UnicodeDecodeError as e:
                            logging.warning(f"Error reading file {file_rel_path}: Encoding issue: {e}. Skipping file.")
                            out_file.write(f"Error reading file: Encoding issue. Content skipped.\n")
                        except Exception as e:
                            logging.warning(f"Error reading file {file_rel_path}: {e}. Skipping file.")
                            out_file.write(f"Error reading file: {str(e)}. Content skipped.\n")

                        out_file.write("\n\n")
    except IOError as e:
        logging.error(f"Error scanning folder: IO error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during folder scan: {e}")

def main(args: List[str]) -> None:
    """
    Main function that handles command-line arguments and initiates the scan.
    Args:
        args (List[str]): Command line arguments, including the path to start scanning, output file, exclusion file, and file extensions.
    """
    if len(args) < 3:
        logging.error("Usage: python script.py <start_path> <output_file> [exclusion_file] [file_extensions...]")
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
        logging.info(f"Using exclusion patterns from {exclusion_file}: {exclusion_patterns}")
    else:
        logging.info("No exclusion file specified. Scanning all files.")

    if file_types:
        logging.info(f"Scanning for file types: {file_types}")
    else:
        logging.info("No file types specified. Scanning all files.")

    scan_folder(start_path, file_types, output_file, exclusion_patterns)
    logging.info(f"Scan complete. Results written to {output_file}")

if __name__ == "__main__":
    main(sys.argv)
