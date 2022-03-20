from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text()
reqs = Path("requirements.txt").read_text().strip().splitlines()

pkg = "git_doc_history"
setup(
    name=pkg,
    version="0.1.1",
    url="https://github.com/seanbreckenridge/git_doc_history",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=(
        """copy/track files in git, and a CLI tool/library to traverse the history"""
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=[pkg]),
    install_requires=reqs,
    package_data={pkg: ["py.typed"]},
    zip_safe=False,
    keywords="data git",
    python_requires=">=3.8",
    scripts=[str(p) for p in Path("bin").glob("*")],
    extras_require={
        "testing": [
            "pytest",
            "mypy",
            "flake8",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
