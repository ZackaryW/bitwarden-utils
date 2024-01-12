from setuptools import setup

setup(
    name="bw-utils",
    version="2.0.0",
    packages=[
        "bitwarden_utils",
        "bitwarden_utils.core",
        "bitwarden_utils.core.models",
        "bitwarden_utils.core.utils",
    ],
    install_requires=[
        "pydantic",
        "click"
    ],
    entry_points={
        "console_scripts": [
            "bwu = bitwarden_utils.cli:cli_main"
        ]
    },
    python_requires=">=3.11",
    author="ZackaryW",
    description="Bitwarden Utilities",
    url="https://github.com/ZackaryW/bitwarden-utils",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        # 3.11 onwards
        "Programming Language :: Python :: 3.11",
    ]
)

