#!/usr/bin/env python3

import os
import re

def fix_syntax_errors(file_path):
    """Fix syntax errors from the previous script"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix escaped quotes
    content = content.replace("\\'", "'")
    
    # Fix extra blank lines in set_version method
    content = re.sub(
        r'def set_version\(self\):\s*\n\s*\n\s*version_path.*?\n\s*\n\s*with open.*?\n\s*\n\s*self\.version.*?\n',
        lambda m: re.sub(r'\n\s*\n', '\n        ', m.group()),
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed syntax errors in {file_path}")
        return True
    return False

def main():
    print("🔧 Fixing syntax errors...")
    
    fixed_count = 0
    for root, dirs, files in os.walk('recipes'):
        for file in files:
            if file == 'conanfile.py':
                file_path = os.path.join(root, file)
                if fix_syntax_errors(file_path):
                    fixed_count += 1
    
    print(f"✅ Fixed syntax errors in {fixed_count} files")

if __name__ == "__main__":
    main()
