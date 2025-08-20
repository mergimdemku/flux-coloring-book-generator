"""
Setup script for Coloring Book Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="coloring-book-generator",
    version="1.0.0",
    author="3D Gravity Kids",
    author_email="info@kopshtimagjik.com",
    description="AI-powered coloring book generator with consistent characters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3dgravitykids/coloring-book-generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Education",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
            "pre-commit>=2.0",
        ],
        "build": [
            "pyinstaller>=5.0",
            "auto-py-to-exe>=2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "coloring-book-generator=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords=[
        "ai",
        "coloring book", 
        "children",
        "art",
        "education",
        "flux",
        "image generation",
        "pdf",
        "desktop app"
    ],
    project_urls={
        "Bug Reports": "https://github.com/3dgravitykids/coloring-book-generator/issues",
        "Source": "https://github.com/3dgravitykids/coloring-book-generator",
        "Documentation": "https://github.com/3dgravitykids/coloring-book-generator/wiki",
    },
)