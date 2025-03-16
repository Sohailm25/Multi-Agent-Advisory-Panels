"""Setup script for the Iterative Research Tool."""

from setuptools import setup, find_packages
import os
import re
from glob import glob

# Read version from __init__.py
with open(os.path.join("iterative_research_tool", "__init__.py"), "r") as f:
    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read())
    version = version_match.group(1) if version_match else "0.0.0"

# Read long description from README
long_description = "Iterative Research Document Generator Tool"
if os.path.exists("README.md"):
    with open("README.md", "r") as f:
        long_description = f.read()

# Package data files
package_data = {
    'iterative_research_tool': ['prompts/*.md'],
}

# Get prompt files to include
prompts = glob('prompts/*.md')

setup(
    name="iterative_research_tool",
    version=version,
    description="Generate exhaustive, textbook-quality research documents through iterative AI enhancement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Iterative Research Tool Team",
    author_email="example@example.com",
    url="https://github.com/example/iterative_research_tool",
    packages=find_packages(),
    include_package_data=True,
    package_data=package_data,
    data_files=[('prompts', prompts)],
    install_requires=[
        # Core dependencies
        "langgraph>=0.0.19",
        "python-dotenv>=1.0.0",
        "requests>=2.25.0",
        "pydantic>=2.4.2,<3.0.0",
        "colorama>=0.4.4",
        "markdown>=3.3.0",
        "tiktoken>=0.4.0",
        "tenacity>=8.0.0",
        "regex>=2022.1.18",
        
        # Default LLM provider
        "anthropic>=0.8.0",
    ],
    extras_require={
        # Optional LLM providers
        "openai": ["openai>=1.3.0"],
        "perplexity": ["perplexity-python>=0.1.0"],
        
        # Install all LLM providers
        "all": [
            "openai>=1.3.0",
            "perplexity-python>=0.1.0",
        ],
        
        # Development dependencies
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "iterative-research=iterative_research_tool.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
) 