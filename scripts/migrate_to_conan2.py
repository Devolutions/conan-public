#!/usr/bin/env python3
"""
Conan 1.x to 2.x Migration Script
Automatically migrates conanfile.py recipes from Conan 1.x to 2.x
"""

import os
import re
import glob
from pathlib import Path

def migrate_imports(content):
    """Migrate import statements from Conan 1.x to 2.x"""
    
    # Replace basic imports
    content = re.sub(r'from conans import ConanFile', 'from conan import ConanFile', content)
    content = re.sub(r'from conans import ([^,\n]+)', r'from conan.legacy import \1', content)
    
    # CMake imports
    if 'CMake' in content:
        if 'from conan.tools.cmake import' not in content:
            content = content.replace('from conan import ConanFile', 
                                    'from conan import ConanFile\nfrom conan.tools.cmake import CMake, cmake_layout')
    
    # Tools imports
    if 'tools.Git' in content or 'Git(' in content:
        if 'from conan.tools.scm import' not in content:
            content = content.replace('from conan import ConanFile', 
                                    'from conan import ConanFile\nfrom conan.tools.scm import Git')
    
    if 'tools.replace_in_file' in content or 'replace_in_file' in content:
        if 'from conan.tools.files import' not in content:
            content = content.replace('from conan import ConanFile', 
                                    'from conan import ConanFile\nfrom conan.tools.files import replace_in_file, copy, load, save')
    
    # Keep legacy imports for compatibility
    if 'tools.' in content:
        if 'from conans import tools' not in content:
            content = content.replace('from conan import ConanFile', 
                                    'from conan import ConanFile\nfrom conans import tools  # Keep for compatibility')
    
    return content

def migrate_version_loading(content):
    """Migrate version loading from file"""
    
    # Replace version loading pattern
    version_pattern = r"version = open\(os\.path\.join\(['\"]?\.['\"]?, ['\"]VERSION['\"]?\), ['\"]r['\"]?\)\.read\(\)\.rstrip\(\)"
    content = re.sub(version_pattern, 
                    'version = load(path=os.path.join(os.path.dirname(__file__), "VERSION")).strip()', 
                    content)
    
    # Add exports_sources for VERSION
    if 'exports = \'VERSION\'' in content:
        content = content.replace('exports = \'VERSION\'', 'exports_sources = "VERSION"')
    
    return content

def migrate_tools_usage(content):
    """Migrate tools.* usage to Conan 2.x equivalents"""
    
    # Git usage
    content = re.sub(r'git = tools\.Git\(folder=([^)]+)\)', r'git = Git(self, folder=\1)', content)
    content = re.sub(r'tools\.Git\(folder=([^)]+)\)', r'Git(self, folder=\1)', content)
    
    # replace_in_file usage  
    content = re.sub(r'tools\.replace_in_file\(([^,]+),\s*([^,]+),\s*([^,)]+)(?:,\s*strict=[^)]+)?\)', 
                    r'replace_in_file(self, \1, \2, \3)', content)
    
    # mkdir usage
    content = re.sub(r'tools\.mkdir\(([^)]+)\)', r'mkdir(self, \1)', content)
    
    return content

def migrate_cmake_usage(content):
    """Migrate CMake usage patterns"""
    
    # Add cmake_layout if CMake is used
    if 'CMake(' in content and 'def layout(self):' not in content:
        # Find the right place to insert layout method (after options/default_options)
        if 'default_options = {' in content:
            content = re.sub(r'(default_options = \{[^}]+\})', 
                           r'\1\n\n    def layout(self):\n        cmake_layout(self)', content)
    
    # Update cmake.configure calls
    content = re.sub(r'cmake\.configure\(source_folder=([^)]+)\)', r'cmake.configure()', content)
    
    return content

def migrate_copy_usage(content):
    """Migrate self.copy() usage to new copy() function"""
    
    # Basic copy patterns
    content = re.sub(r'self\.copy\(([^,]+), dst=([^,)]+)(?:, keep_path=False)?\)', 
                    r'copy(self, \1, dst=os.path.join(self.package_folder, \2), src=self.build_folder)', content)
    
    content = re.sub(r'self\.copy\(([^,]+), src=([^,]+), dst=([^)]+)\)', 
                    r'copy(self, \1, src=os.path.join(self.source_folder, \2), dst=os.path.join(self.package_folder, \3))', content)
    
    content = re.sub(r'self\.copy\(([^)]+)\)', 
                    r'copy(self, \1, dst=self.package_folder, src=self.build_folder)', content)
    
    return content

def migrate_dependencies_access(content):
    """Migrate dependencies access patterns"""
    
    # This is more complex and may need manual intervention
    # deps_cpp_info patterns need to be migrated to self.dependencies
    if 'deps_cpp_info' in content:
        print("    WARNING: deps_cpp_info usage found - may need manual migration")
    
    return content

def add_layout_method(content):
    """Add layout method if missing"""
    
    if 'def layout(self):' not in content and ('CMake' in content or 'cmake' in content.lower()):
        # Find insertion point after default_options
        if 'default_options = {' in content:
            content = re.sub(r'(\s+}\s*\n)', 
                           r'\1\n    def layout(self):\n        cmake_layout(self)\n', content)
    
    return content

def migrate_conanfile(file_path):
    """Migrate a single conanfile.py"""
    
    print(f"Migrating {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Apply all migrations
    content = migrate_imports(content)
    content = migrate_version_loading(content)
    content = migrate_tools_usage(content)
    content = migrate_cmake_usage(content)
    content = migrate_copy_usage(content)
    content = migrate_dependencies_access(content)
    content = add_layout_method(content)
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"    ✓ Migrated {file_path}")
        return True
    else:
        print(f"    - No changes needed for {file_path}")
        return False

def main():
    """Main migration function"""
    
    print("🚀 Starting Conan 1.x to 2.x Migration")
    print("=" * 50)
    
    # Find all conanfile.py files
    recipe_pattern = "recipes/*/conanfile.py"
    test_pattern = "recipes/*/test_package/conanfile.py"
    
    conanfiles = glob.glob(recipe_pattern) + glob.glob(test_pattern)
    
    print(f"Found {len(conanfiles)} conanfile.py files to migrate")
    print()
    
    migrated_count = 0
    
    for conanfile in conanfiles:
        if migrate_conanfile(conanfile):
            migrated_count += 1
    
    print()
    print("=" * 50)
    print(f"✅ Migration complete!")
    print(f"📊 Migrated {migrated_count}/{len(conanfiles)} files")
    print()
    print("⚠️  Manual review needed for:")
    print("   - deps_cpp_info usage (now self.dependencies)")
    print("   - Complex tools usage") 
    print("   - Generator specifications")
    print("   - Build requirements method signatures")

if __name__ == "__main__":
    main()
