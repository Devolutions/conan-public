#!/usr/bin/env python3
"""
Fix deps_cpp_info usage in Conan 2.x migration
"""

import os
import re
import glob

def fix_deps_cpp_info(content):
    """Fix deps_cpp_info usage patterns"""
    
    # Pattern: self.deps_cpp_info['package'].rootpath
    content = re.sub(r"self\.deps_cpp_info\['([^']+)'\]\.rootpath", 
                    r"self.dependencies['\1'].package_folder", content)
    
    # Pattern: self.deps_cpp_info['package'].libdirs[0]
    content = re.sub(r"self\.deps_cpp_info\['([^']+)'\]\.libdirs\[0\]", 
                    r'"lib"', content)  # Most packages use 'lib' as libdir
    
    # Pattern: self.deps_cpp_info['package'].includedirs[0]
    content = re.sub(r"self\.deps_cpp_info\['([^']+)'\]\.includedirs\[0\]", 
                    r'"include"', content)  # Most packages use 'include' as includedir
    
    return content

def fix_deps_env_info(content):
    """Fix deps_env_info usage patterns"""
    
    # This is more complex and needs manual review
    if 'deps_env_info' in content:
        print("    WARNING: deps_env_info usage found - needs manual migration")
        
        # Basic pattern for cbake
        content = re.sub(r'self\.deps_env_info\["cbake"\]\.CBAKE_HOME', 
                        r'self.dependencies["cbake"].package_folder', content)
        
        content = re.sub(r'self\.deps_env_info\["sysroot"\]\.CMAKE_SYSROOT', 
                        r'self.dependencies["sysroot"].package_folder', content)
    
    return content

def fix_file(file_path):
    """Fix a single file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    if 'deps_cpp_info' in content or 'deps_env_info' in content:
        print(f"Fixing dependencies in {file_path}")
        content = fix_deps_cpp_info(content)
        content = fix_deps_env_info(content)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"    ✓ Fixed {file_path}")
            return True
    
    return False

def main():
    """Main function"""
    
    print("🔧 Fixing deps_cpp_info usage for Conan 2.x")
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
