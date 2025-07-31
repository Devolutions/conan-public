#!/usr/bin/env python3

import os
import re
import glob

def fix_conanfile_imports_and_version(file_path):
    """Fix common Conan 2.x import and version loading issues"""
    
    print(f"Fixing {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix problematic imports
    content = re.sub(r'from conans import tools.*\n', '', content)
    content = re.sub(r'from conan\.legacy import tools.*\n', '', content)
    
    # Fix duplicate imports
    lines = content.split('\n')
    seen_imports = set()
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('from conan.tools') or line.strip().startswith('from conan import'):
            if line not in seen_imports:
                seen_imports.add(line)
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Fix version loading - look for version = load(...) pattern at class level
    content = re.sub(
        r'(\s+)version = load\(.*?\)\.strip\(\)\n(\s+)(.*?)\n(\s+)tag = [\'"]v[\'"] \+ version',
        r'\1\3\n\1\n\1def set_version(self):\n\1    version_path = os.path.join(os.path.dirname(__file__), "VERSION")\n\1    with open(version_path, \'r\') as f:\n\1        self.version = f.read().strip()\n\1        self.tag = "v" + self.version',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Fix standalone version loading
    content = re.sub(
        r'(\s+)version = load\(.*?\)\.strip\(\)',
        r'\1\n\1def set_version(self):\n\1    version_path = os.path.join(os.path.dirname(__file__), "VERSION")\n\1    with open(version_path, \'r\') as f:\n\1        self.version = f.read().strip()',
        content
    )
    
    # Fix tools.which calls
    content = re.sub(r'tools\.which\(', r'shutil.which(', content)
    
    # Ensure shutil is imported if we're using shutil.which
    if 'shutil.which' in content and 'import shutil' not in content:
        # Add shutil import after other imports
        import_pattern = r'(from conan.*?\n)+(\n*)(import.*?\n)+'
        match = re.search(import_pattern, content, re.MULTILINE)
        if match:
            end_pos = match.end()
            if 'import shutil' not in match.group():
                content = content[:end_pos] + 'import shutil\n' + content[end_pos:]
    
    # Write back only if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"    ✓ Fixed {file_path}")
        return True
    else:
        print(f"    - No changes needed for {file_path}")
        return False

def main():
    print("🔧 Fixing import and version loading issues")
    print("=" * 50)
    
    # Find all conanfile.py files
    conanfiles = []
    for root, dirs, files in os.walk('recipes'):
        for file in files:
            if file == 'conanfile.py':
                conanfiles.append(os.path.join(root, file))
    
    print(f"Found {len(conanfiles)} conanfile.py files to fix\n")
    
    fixed_count = 0
    for conanfile in sorted(conanfiles):
        if fix_conanfile_imports_and_version(conanfile):
            fixed_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Fixing complete!")
    print(f"📊 Fixed {fixed_count}/{len(conanfiles)} files")

if __name__ == "__main__":
    main()
