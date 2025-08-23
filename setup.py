import os
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


class PostInstallDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        self._install_playwright_browsers()


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        self._install_playwright_browsers()
    
    def _install_playwright_browsers(self):
        """Install Playwright browsers after package installation."""
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install"])
            print("✓ Playwright browsers installed successfully")
        except subprocess.CalledProcessError:
            print("⚠ Warning: Failed to install Playwright browsers automatically.")
            print("  You may need to run 'playwright install' manually.")

setup(
    name="cesail",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0",
        "pytest>=8.0.0",
        "pytest-asyncio>=0.23.0",
        "pydantic>=2.0.0",
        "fastmcp>=2.0.0",
        "openai>=1.0.0",
        "tenacity>=8.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
        ]
    },
    python_requires=">=3.9",
    author="Rachita Pradeep",
    author_email="ajjayawardane@gmail.com",
    description="A comprehensive web automation and DOM parsing platform with AI-powered agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AkilaJay/cesail",
    cmdclass={
        'develop': PostInstallDevelopCommand,
        'install': PostInstallCommand,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
) 