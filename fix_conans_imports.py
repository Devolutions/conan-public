#!/usr/bin/env python3
"""
Fix all remaining 'from conans import tools' imports that are incompatible with Conan 2.x
"""

import os
import re
import glob

def fix_conans_imports(file_path):
    """Remove unused 'from conans import tools' lines from conanfile.py"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove the problematic import line
    content = re.sub(r'from conans import tools  # Keep for compatibility\n', '', content)
    
    # Also remove any other conans imports that might be problematic
    content = re.sub(r'from conans import tools\n', '', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def main():
    # Find all conanfile.py files in recipes directory
    pattern = "recipes/**/conanfile.py"
    files = glob.glob(pattern, recursive=True)
    
    print(f"Found {len(files)} conanfile.py files")
    
    for file_path in files:
        # Check if file contains the problematic import
        with open(file_path, 'r') as f:
            content = f.read()
        
        if 'from conans import tools' in content:
            fix_conans_imports(file_path)
        else:
            print(f"Skipped {file_path} (no conans import)")

if __name__ == "__main__":
    main()
