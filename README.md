Reflex starter template

## Dependency Management Rules

### Package Manager Requirements
- **MANDATORY**: Use UV for all Python package operations
- **NEVER** use `pip` directly - always use `uv pip` commands
- UV provides faster, more reliable dependency resolution and package management

### Version Specification Policy
- **DISALLOWED**: Hard-pinned versions (e.g., `fastapi==0.110.0`)
- **REQUIRED**: Use minimum version specifiers with no upper bound (e.g., `fastapi>=0.110`)
- This ensures compatibility with newest versions while maintaining minimum requirements
- Exception: Only pin exact versions for security-critical packages when absolutely necessary

### Dependency Management Workflow

#### Adding New Packages
```bash
# Add a new package with minimum version
uv pip install "package_name>=minimum_version"

# Example: Adding FastAPI
uv pip install "fastapi>=0.110"

# For packages with extras
uv pip install "package_name[extra1,extra2]>=minimum_version"
```

#### Removing Packages
```bash
# Remove a package
uv pip uninstall package_name

# Remove multiple packages
uv pip uninstall package1 package2 package3
```

#### Synchronizing Dependencies
```bash
# Sync all dependencies from requirements.txt
uv pip sync requirements.txt

# Install all packages from requirements.txt
uv pip install -r requirements.txt
```

#### Dependency Health Checks
```bash
# Check for dependency conflicts and compatibility issues
uv pip check

# List installed packages and versions
uv pip list

# Show dependency tree
uv pip show --verbose package_name
```

### Maintenance Schedule
- **Weekly**: Run `uv pip check` to identify dependency conflicts
- **Monthly**: Review and update minimum version requirements
- **Before releases**: Ensure all dependencies use newest compatible versions

### Best Practices
1. Always test with newest compatible versions in development
2. Use virtual environments for isolation: `uv venv` and `source .venv/bin/activate`
3. Keep `requirements.txt` updated with all production dependencies
4. Document any version constraints with justification in comments
5. Regular dependency audits for security vulnerabilities
