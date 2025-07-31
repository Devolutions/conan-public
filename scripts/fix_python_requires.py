#!/usr/bin/env python3
"""
Fix python_requires for Conan 2.x
"""

import os
import re
import glob

def fix_python_requires(content):
    """Fix python_requires usage patterns"""
    
    # Pattern: python_requires = "shared/1.0.0@devolutions/stable"
    content = re.sub(r'python_requires = "([^/]+)/([^@]+)@([^"]+)"', 
                    r'python_requires = "\1/[\2]@\3"', content)
    
    return content

def fix_file(file_path):
    """Fix a single file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    if 'python_requires = "' in content:
        print(f"Fixing python_requires in {file_path}")
        content = fix_python_requires(content)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"    ✓ Fixed {file_path}")
            return True
    
    return False

def main():
    """Main function"""
    
    print("🔧 Fixing python_requires usage for Conan 2.x")
    print("=" * 50)
    
    # Find all conanfile.py files
    conanfiles = glob.glob("recipes/*/conanfile.py")
    
    fixed_count = 0
    
    for conanfile in conanfiles:
        if fix_file(conanfile):
            fixed_count += 1
    
    print()
    print(f"✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
