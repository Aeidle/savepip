from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="savepip",
    version="0.2.0",
    author="ADIL ALAMI",
    author_email="adilalami707@gmail.com",
    description="A tool to install and save clean package dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aeidle/savepip",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyyaml>=5.1",
    ],
    entry_points={
        "console_scripts": [
            "savepip=savepip.cli:main",
        ],
    },
)
