# Migration Scripts

This directory contains helper Python scripts used during the Conan 1.x to 2.x migration process.

## Scripts Overview

### Core Migration Scripts

- **`migrate_to_conan2.py`** - Main migration script that converts Conan 1.x recipes to 2.x format
  - Updates imports (conans → conan)
  - Converts tools usage to new patterns
  - Fixes CMake, copy, and version loading patterns
  - Processes 46+ conanfile.py recipes automatically


### Dependency & Requirements Scripts

- **`fix_dependencies.py`** - Converts dependency access patterns
  - Changes `deps_cpp_info` to `self.dependencies`
  - Updates library and include path access
  - Fixes dependency information retrieval

- **`fix_requirements.py`** - Updates requirements declarations
  - Converts `build_requires` to `tool_requires`
  - Fixes requirement method signatures
  - Updates requirement syntax for Conan 2.x

- **`fix_python_requires.py`** - Fixes Python requirements and version ranges
  - Updates version range syntax
  - Fixes python_requires declarations
  - Ensures compatibility with Conan 2.x version handling

### Import & Syntax Cleanup Scripts

- **`clean_imports.py`** - Cleans up import statements
  - Removes invalid imports from conan.tools modules
  - Eliminates duplicate import statements
  - Fixes import conflicts between Conan 1.x and 2.x

- **`fix_conan2_issues.py`** - Comprehensive import and version loading fixes
  - Removes problematic `from conans import tools`
  - Fixes version loading patterns (load() → file reading)
  - Updates tools.which() to shutil.which()
  - Handles duplicate import removal

- **`fix_syntax_errors.py`** - Fixes syntax errors from migration scripts
  - Corrects escaped quote issues
  - Cleans up formatting in set_version() methods
  - Fixes indentation and spacing issues

## Usage

These scripts were run in sequence during the migration:

```bash
# 1. Main migration
python3 scripts/migrate_to_conan2.py

# 2. Fix specific patterns
python3 scripts/fix_dependencies.py
python3 scripts/fix_requirements.py
python3 scripts/fix_python_requires.py

# 3. Clean up issues
python3 scripts/fix_conan2_issues.py
python3 scripts/fix_syntax_errors.py
python3 scripts/clean_imports.py
```

## Migration Results

- ✅ 46 conanfile.py recipes migrated
- ✅ GitHub Actions workflow updated (Conan 1.66.0 → 2.19.1)
- ✅ PowerShell build scripts updated
- ✅ Settings.yml updated for GCC 11+ support
- ✅ Successfully tested: shared, zlib, cbake packages

## Notes

- Scripts are designed to be idempotent (safe to run multiple times)
- Always review changes before committing
- Some recipes may need manual tweaking for complex cases
- These scripts represent the complete migration from Conan 1.x maintenance mode to modern Conan 2.x
