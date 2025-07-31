#!/usr/bin/env python3

import os
import re

def clean_imports(file_path):
    """Clean up import statements to be Conan 2.x compatible"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix import lines
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip problematic imports entirely
        if 'from conans import' in line:
            continue
        if 'from conan.legacy import' in line:
            continue
        
        # Fix specific import issues
        if 'from conan.tools.cmake import' in line:
            # Remove invalid imports from cmake
            line = re.sub(r', tools', '', line)
            line = re.sub(r', python_requires', '', line)
            line = re.sub(r'tools, ', '', line)
            line = re.sub(r'python_requires, ', '', line)
            # Remove duplicates
            parts = line.split('import ')[1].split(', ')
            unique_parts = []
            for part in parts:
                part = part.strip()
                if part and part not in unique_parts:
                    unique_parts.append(part)
            if unique_parts:
                line = f"from conan.tools.cmake import {', '.join(unique_parts)}"
        
        # Fix scm imports
        if 'from conan.tools.scm import' in line:
            line = re.sub(r', tools', '', line)
            line = re.sub(r'tools, ', '', line)
        
        # Fix files imports
        if 'from conan.tools.files import' in line:
            line = re.sub(r', tools', '', line)
            line = re.sub(r'tools, ', '', line)
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Remove empty import lines
    content = re.sub(r'from [^\\n]+ import\s*\n', '', content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Cleaned imports in {file_path}")
        return True
    return False

def main():
    print("🧹 Cleaning up import statements...")
    
    fixed_count = 0
    for root, dirs, files in os.walk('recipes'):
        for file in files:
            if file == 'conanfile.py':
                file_path = os.path.join(root, file)
                if clean_imports(file_path):
                    fixed_count += 1
    
    print(f"✅ Cleaned imports in {fixed_count} files")

if __name__ == "__main__":
    main()
