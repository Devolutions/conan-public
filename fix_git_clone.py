#!/usr/bin/env python3
"""
Fix Git.clone() syntax for Conan 2.x compatibility across all recipes.
Changes from positional arguments to keyword arguments as required by Conan 2.x.
"""
import os
import re
import glob

def fix_git_clone_in_file(file_path):
    """Fix Git.clone() syntax in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: git.clone(self.url, self.branch) -> git.clone(url=self.url, target=".") + git.checkout(commit=self.branch)
    pattern1 = r'(\s+)git\.clone\(self\.url,\s*self\.branch\)'
    def replace1(match):
        indent = match.group(1)
        return f'{indent}git.clone(url=self.url, target=".")\n{indent}git.checkout(commit=self.branch)'
    content = re.sub(pattern1, replace1, content)
    
    # Pattern 2: git.clone(self.url) -> git.clone(url=self.url, target=".")
    # Only do this if there's already a checkout call afterwards
    pattern2 = r'(\s+)git\.clone\(self\.url\)(\s+git\.checkout\([^)]+\))'
    def replace2(match):
        indent = match.group(1)
        checkout = match.group(2)
        return f'{indent}git.clone(url=self.url, target="."){checkout}'
    content = re.sub(pattern2, replace2, content)
    
    # Pattern 3: git.clone(self.url) without checkout -> git.clone(url=self.url, target=".")
    pattern3 = r'(\s+)git\.clone\(self\.url\)(?!\s+git\.checkout)'
    def replace3(match):
        indent = match.group(1)
        return f'{indent}git.clone(url=self.url, target=".")'
    content = re.sub(pattern3, replace3, content)
    
    # Pattern 4: git.clone("literal_url") -> git.clone(url="literal_url", target=".")
    pattern4 = r'(\s+)git\.clone\("([^"]+)"\)'
    def replace4(match):
        indent = match.group(1)
        url = match.group(2)
        return f'{indent}git.clone(url="{url}", target=".")'
    content = re.sub(pattern4, replace4, content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix Git.clone() syntax in all recipe files."""
    recipe_files = glob.glob('recipes/*/conanfile.py')
    fixed_files = []
    
    for file_path in recipe_files:
        if fix_git_clone_in_file(file_path):
            fixed_files.append(file_path)
            print(f"Fixed: {file_path}")
    
    if fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for file_path in fixed_files:
            print(f"  {file_path}")
    else:
        print("No files needed fixing.")

if __name__ == '__main__':
    main()
