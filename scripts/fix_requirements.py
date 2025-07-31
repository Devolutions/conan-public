#!/usr/bin/env python3
"""
Fix build_requires to tool_requires for Conan 2.x
"""

import os
import re
import glob

def fix_build_requires(content):
    """Fix build_requires usage patterns"""
    
    # Replace build_requires with tool_requires (for build tools)
    # Pattern: self.build_requires('package/version@user/channel')
    content = re.sub(r"self\.build_requires\('([^/]+)/([^@]+)@([^']+)'\)", 
                    r"self.tool_requires('\1/[\2]@\3')", content)
    
    # Replace 'latest' with [*] for version ranges
    content = re.sub(r"/\[latest\]@", r"/[*]@", content)
    
    return content

def fix_requires(content):
    """Fix requires usage patterns"""
    
    # Regular dependencies should use requires, not tool_requires
    # Look for requires = statements (these are regular dependencies)
    content = re.sub(r"requires = '([^/]+)/([^@]+)@([^']+)'", 
                    r"requires = '\1/[\2]@\3'", content)
    
    return content

def fix_file(file_path):
    """Fix a single file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    if 'build_requires' in content or "requires = '" in content:
        print(f"Fixing requirements in {file_path}")
        content = fix_build_requires(content)
        content = fix_requires(content)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"    ✓ Fixed {file_path}")
            return True
    
    return False

def main():
    """Main function"""
    
    print("🔧 Fixing build_requires usage for Conan 2.x")
    print("=" * 50)
    
    # Find all conanfile.py files
    conanfiles = glob.glob("recipes/*/conanfile.py") + glob.glob("recipes/*/test_package/conanfile.py")
    
    fixed_count = 0
    
    for conanfile in conanfiles:
        if fix_file(conanfile):
            fixed_count += 1
    
    print()
    print(f"✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
