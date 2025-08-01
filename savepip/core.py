#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import json
import re
from datetime import datetime
from .memory_manager import MemoryManager


class DependencySaver:
    def __init__(self, output_file=None, manager="pip", memory_manager=None):
        self.manager = manager.lower()
        self.output_file = output_file or self._get_default_output_file()
        self.packages = []
        self.memory_manager = memory_manager or MemoryManager()

    def _get_default_output_file(self):
        if self.manager == "pip":
            return "requirements.txt"
        elif self.manager == "conda":
            return "environment.yml"
        else:
            raise ValueError(f"Unsupported package manager: {self.manager}")
    
    def install_and_save(self, packages, upgrade=False, dev=False):
        """Install packages and save dependencies to file"""
        if not packages:
            print("No packages specified for installation.")
            return False
            
        self.packages = packages
        # Install the packages
        success = self._install_packages(packages, upgrade)
        if not success:
            return False
            
        # Save dependencies
        for package in packages:
            self.memory_manager.add_dependency(package)
        return self._save_dependencies(dev)

    def _install_packages(self, packages, upgrade=False):
        """Install packages using the specified package manager"""

        try:
            if self.manager == "pip":
                cmd = [sys.executable, "-m", "pip", "install"]
                if upgrade:
                    cmd.append("--upgrade")
                cmd.extend(packages)
            elif self.manager == "conda":
                cmd = ["conda", "install"]
                if upgrade:
                    cmd.append("--update-all")
                cmd.extend(packages)
                cmd.append("-y")
            else:
                raise ValueError(f"Unsupported package manager: {self.manager}")
                
            subprocess.check_call(cmd)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            return False
    
    def _save_dependencies(self, dev=False, categories=None):
        """Save dependencies to file"""

        try:
            if self.manager == "pip":
                target_packages = {pkg.lower() for pkg in self.memory_manager.get_dependencies(categories)}
                return self._save_pip_dependencies(dev, target_packages)
            elif self.manager == "conda":
                return self._save_conda_dependencies(categories)
            else:
                raise ValueError(f"Unsupported package manager: {self.manager}")
        except Exception as e:
            print(f"Error saving dependencies: {e}")
            return False
    
    def _save_pip_dependencies(self, dev=False, target_packages=None):
        """Save pip dependencies to requirements.txt"""

        try:
            # Dictionary to store final requirements (package_name: full_requirement_line)
            final_requirements = {}
            
            # Dictionary to track all installed packages (name: version)
            all_installed_packages = {}
            
            # Get list of all installed packages
            cmd = [sys.executable, "-m", "pip", "list", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                try:
                    installed_pkgs = json.loads(result.stdout)
                    for pkg in installed_pkgs:
                        pkg_name = pkg['name'].lower()
                        version = pkg['version']
                        # Skip Python standard library packages and development packages
                        if pkg_name not in ['pip', 'setuptools', 'wheel', 'distribut']:
                            all_installed_packages[pkg_name] = version
                except json.JSONDecodeError:
                    pass
            else:
                pass
            
            # Load existing requirements if file exists
            existing_packages = {}
            existing_package_names = set()
            if os.path.exists(self.output_file):

                with open(self.output_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Store as {package_name: full_requirement_line}
                            pkg_name = line.split('==')[0].lower()
                            existing_packages[pkg_name] = line
                            existing_package_names.add(pkg_name)

            
            # Process packages from memory manager (target_packages)
            for pkg_name in target_packages:
                # Run pip show to get the version
                try:
                    cmd = [sys.executable, "-m", "pip", "show", pkg_name]

                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Extract version from pip show output
                        version = None
                        for line in result.stdout.strip().split('\n'):
                            if line.startswith('Version:'):
                                version = line.split('Version:')[1].strip()
                                break
                        
                        if version:
                            # Clean up the version (remove +dev, etc.)
                            version = re.sub(r'(\d+\.\d+\.\d+)\+.*', r'\1', version)
                            req_line = f"{pkg_name}=={version}"
                            final_requirements[pkg_name] = req_line
                    else:
                        continue
                except Exception:
                    continue
            
            # Process packages from existing requirements.txt
            for pkg_name, req_line in existing_packages.items():
                if pkg_name not in final_requirements:
                    try:
                        # Check if package is installed (using our all_installed_packages first)
                        if pkg_name in all_installed_packages:
                            version = all_installed_packages[pkg_name]
                            # Clean up the version (remove +dev, etc.)
                            version = re.sub(r'(\d+\.\d+\.\d+)\+.*', r'\1', version)
                            updated_req_line = f"{pkg_name}=={version}"
                            final_requirements[pkg_name] = updated_req_line
                            
                            # Add installed package to memory manager
                            self.memory_manager.add_dependency(pkg_name)
                        else:
                            # Fallback to pip show if not found in all_installed_packages
                            cmd = [sys.executable, "-m", "pip", "show", pkg_name]

                            result = subprocess.run(cmd, capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                # Extract version from pip show output
                                version = None
                                for line in result.stdout.strip().split('\n'):
                                    if line.startswith('Version:'):
                                        version = line.split('Version:')[1].strip()
                                        break
                                
                                if version:
                                    # Clean up the version (remove +dev, etc.)
                                    version = re.sub(r'(\d+\.\d+\.\d+)\+.*', r'\1', version)
                                    updated_req_line = f"{pkg_name}=={version}"
                                    final_requirements[pkg_name] = updated_req_line
                                    
                                    # Add installed package to memory manager
                                    self.memory_manager.add_dependency(pkg_name)
                                else:
                                    # Keep original line if can't extract version
                                    final_requirements[pkg_name] = req_line

                            else:
                                # Package not installed but was in requirements.txt, so keep it
                                final_requirements[pkg_name] = req_line
                                
                                # Add to memory manager so it's tracked for future installs
                                self.memory_manager.add_dependency(pkg_name)
                    except Exception as e:
                        # On error, keep the original requirement
                        final_requirements[pkg_name] = req_line
                        # On error, keep the original requirement
            

            
            # Convert final_requirements dictionary to sorted list
            cleaned_requirements = list(final_requirements.values())
            cleaned_requirements.sort(key=lambda x: x.lower())
            
            # Final sort by package name
            cleaned_requirements.sort(key=lambda x: x.lower())
            
            # Add header comment
            header = f"# Requirements generated by pipsave on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Write to file
            with open(self.output_file, 'w') as f:
                f.write(header)
                f.write('\n'.join(cleaned_requirements))
                f.write('\n')
                

            print(f"Dependencies saved to {self.output_file}")
            return True
        except Exception as e:
            print(f"Error saving pip dependencies: {e}")
            return False
    
    def _save_conda_dependencies(self, categories=None):

        try:
            # Load existing environment if file exists
            existing_deps = set()
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r') as f:
                    existing_env = yaml.safe_load(f)
                    if existing_env and 'dependencies' in existing_env:
                        for dep in existing_env['dependencies']:
                            if isinstance(dep, str):
                                existing_deps.add(dep.lower())
                            elif isinstance(dep, dict) and 'pip' in dep:
                                for pip_dep in dep['pip']:
                                    existing_deps.add(pip_dep.lower())
            
            # Get environment info
            cmd = ["conda", "env", "export"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            env_data = result.stdout
            
            # Parse YAML content
            import yaml
            env_dict = yaml.safe_load(env_data)
            
            # Keep only essential info and target packages
            cleaned_dict = {
                'name': env_dict.get('name', 'base'),
                'channels': ['defaults'],
                'dependencies': []
            }
            
            # Convert packages list to lowercase for case-insensitive comparison
            target_packages = {pkg.lower() for pkg in self.memory_manager.get_dependencies(categories)}
            
            if 'dependencies' in env_dict:
                for dep in env_dict['dependencies']:
                    if isinstance(dep, str):
                        pkg_name = dep.split('=')[0].lower()
                        if pkg_name in target_packages or dep.lower() in existing_deps:
                            # Remove build hash if present
                            dep = re.sub(r'=\d+\.\d+\.\d+=.*', lambda m: m.group(0).split('=')[0] + '=' + m.group(0).split('=')[1], dep)
                            cleaned_dict['dependencies'].append(dep)
                    elif isinstance(dep, dict) and 'pip' in dep:
                        # Handle pip dependencies
                        pip_deps = []
                        for pip_dep in dep['pip']:
                            pkg_name = pip_dep.split('==')[0].lower()
                            if pkg_name in target_packages:
                                pip_dep = re.sub(r'(==\d+\.\d+\.\d+)\+.*', r'\1', pip_dep)
                                pip_deps.append(pip_dep)
                        if pip_deps:
                            pip_deps.sort(key=lambda x: x.lower())
                            cleaned_dict['dependencies'].append({'pip': pip_deps})
            
            # Add header comment
            header = f"# Environment generated by pipsave on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Write to file
            with open(self.output_file, 'w') as f:
                f.write(header)
                yaml.dump(cleaned_dict, f, default_flow_style=False)
                
            print(f"Dependencies saved to {self.output_file}")
            return True
        except ImportError:
            print("Error: PyYAML is required for conda dependency saving. Install with 'pip install pyyaml'")
            return False
        except Exception as e:
            print(f"Error saving conda dependencies: {e}")
            return False
