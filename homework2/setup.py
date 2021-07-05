from os.path import dirname, join

from setuptools import find_packages, setup

setup(
    name='mygrep',
    description='',
    version='1.0',
    author='sakost',
    author_email='example@gmail.com',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    entry_points={'console_scripts': ['mygrep = myapp.app:main']},
)
