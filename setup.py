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
        "anthropic>=0.9.0",
        "requests>=2.25.0",
        "pydantic>=1.10.0,<2.0.0",  # Use v1 for compatibility
        "colorama>=0.4.4",  # For terminal colors
        "markdown>=3.3.0",
        "tiktoken>=0.4.0",  # For token counting
        "tenacity>=8.0.0",  # For retries
        "regex>=2022.1.18",  # For advanced regex in prompt extraction
        "python-dotenv>=0.21.0",  # For loading environment variables
        "langgraph>=0.0.19",  # For orchestration flows
    ],
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
) 