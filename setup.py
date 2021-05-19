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
    long_description = open(readme, "r").read()
except IOError:
    logger.warning("README file not found or unreadable.")
    long_description = "See https://github.com/brunns/mbtest/"

install_dependencies = [
    "requests~=2.0",
    "furl~=2.0",
    "pyhamcrest~=2.0",
    "Deprecated~=1.2",
    "brunns-matchers~=2.4",
]
test_dependencies = [
    "pytest~=6.0",
    "contexttimer~=0.3",
    "brunns-builder~=0.6",
    "trustme~=0.7",
]
coverage_dependencies = [
    "pytest-cov~=2.5",
    "codacy-coverage~=1.0",
]
docs_dependencies = [
    "sphinx>=2.4,<5.0",
    "sphinx-autodoc-typehints~=1.10",
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
    version="2.8.0",
    description="Python wrapper & utils for the Mountebank over the wire test double tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Simon Brunning",
    author_email="simon@brunningonline.net",
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.6",
    install_requires=install_dependencies,
    tests_require=test_dependencies,
    extras_require=extras,
)
