from setuptools import setup, find_packages

setup(
    name='bwUtil',
    version='0.2',
    packages=[
        'bwUtil',
        'bwUtil.caller',
        'bwUtil.download',
        'bwUtilGui',
        'bwUtilCli',
    ],
    url="https://github.com/ZackaryW/bitwarden-utils",
    license='MIT',
    author='Zackary W',
    description='bitwarden utilities',
    install_requires=[
        'requests',
    ],
    # other install commands
    extras_require= {
        'gui' : [
            'PySide6',
            'qt-material'
        ],
        'cli' : [
            'click',
        ],
        "all" : [
            'PySide6',
            'click',
            'qt-material'
        ]
    },
    entry_points={
        'console_scripts': [
            'bwUtilCli = bwUtilCli.__init__:main',
            'bwUtilGui = bwUtilGui.__init__:create_app',
        ],
    }
)

