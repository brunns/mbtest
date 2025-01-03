import logging
import os

from setuptools import find_packages, setup

logger = logging.getLogger(__name__)

# Get the base directory
here = os.path.dirname(__file__)
if not here:
    here = os.path.curdir
here = os.path.abspath(here)

try:
    readme = os.path.join(here, "README.md")
    long_description = open(readme).read()
except OSError:
    logger.warning("README file not found or unreadable.")
    long_description = "See https://github.com/brunns/mbtest/"

install_dependencies = [
    "pyhamcrest>=2.0",
    "Deprecated>=1.2",
    "brunns-matchers>=2.9",
    "yarl>=1.9",
    "httpx>=0.28",
]
test_dependencies = [
    "pytest>=6.0",
    "contexttimer>=0.3",
    "brunns-builder>=1.1",
    "trustme>=0.9",
    "furl>=2.0",
]
coverage_dependencies = [
    "pytest-cov>=2.5",
    "codacy-coverage>=1.0",
]
docs_dependencies = [
    "sphinx>=3.0",
    "sphinx-autodoc-typehints>=1.10",
    "pytest>=6.0",
    "furo",
]

extras = {
    "install": install_dependencies,
    "test": test_dependencies,
    "coverage": coverage_dependencies,
    "docs": docs_dependencies,
}

setup(
    name="mbtest",
    zip_safe=False,
    version="2.14.0",
    description="Python wrapper & utils for the Mountebank over the wire test double tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Simon Brunning",
    author_email="simon@brunn.ing",
    url="https://github.com/brunns/mbtest/",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["README.md"], "mbtest": ["py.typed"]},
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.9",
    install_requires=install_dependencies,
    tests_require=test_dependencies,
    extras_require=extras,
)
