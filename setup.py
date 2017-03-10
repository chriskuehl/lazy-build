from setuptools import find_packages
from setuptools import setup


setup(
    name='lazy-build',
    version='0.1.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=['boto3'],
    packages=find_packages(exclude=('tests*', 'testing*')),
    entry_points={
        'console_scripts': ['lazy-build = lazy_build.cli:main'],
    },
)
