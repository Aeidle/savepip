# SavePip

A tool to intelligently install and save clean package dependencies for both pip and conda environments.

## Installation

```bash
pip install savepip
```

## Usage
```bash
# Install packages with pip
savepip install pandas numpy

# Install packages with conda
savepip -m conda numpy pandas

# Save current environment
savepip save

# Upgrade packages
savepip -u requests pandas

# Save to custom file
savepip -o custom_requirements.txt requests pandas
```

## Features

- **Smart Dependency Management**: Tracks installed packages in a memory file for future reference
- **Requirements.txt Preservation**: Maintains packages in requirements.txt even if not in memory
- **Selective Package Tracking**: Only includes packages explicitly installed with savepip or already in requirements.txt
- **Synchronization**: Automatically syncs memory with requirements.txt content
- **Clean Output**: Removes build hashes, development versions, and unnecessary information
- **Package Manager Support**: Works with both pip and conda environments
- **Alphabetical Sorting**: Dependencies are sorted alphabetically for readability

## How It Works

SavePip maintains a memory of installed packages in `.savepip/memory.json` and uses this to:

1. Track packages explicitly installed with savepip
2. Preserve packages already in requirements.txt
3. Update package versions when they change
4. Generate clean requirements files

Unlike `pip freeze`, savepip only includes packages you've specifically chosen to track, avoiding bloated requirements files with unnecessary dependencies.

## Category Management

SavePip supports organizing packages into categories, allowing you to manage different sets of dependencies for different purposes:

```bash
# Create a new category
savepip mk-category dev

# Switch to a category
savepip use-category dev

# Show current category
savepip cur-category

# List all categories
savepip ls-category

# Install packages to the current category
savepip install pytest coverage

# Save dependencies from specific categories
savepip save --categories dev,prod
```

This feature is useful for managing different types of dependencies (e.g., development, production, testing) within the same project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contribution

We welcome contributions! Feel free to submit issues or pull requests.
