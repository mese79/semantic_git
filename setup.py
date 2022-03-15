import os
from setuptools import setup, find_packages


version = '0.1.1'

description = 'Git commands in plain english'
cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README.md')).read()
except Exception:
    long_description = description

setup(
    name='semantic_git',
    version=version,
    author='Mehdi Seifi',
    author_email='mehdiseifi@gmail.com',
    license='MIT',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mese79/semantic_git/',
    project_urls={
        "Bug Tracker": "https://github.com/mese79/semantic_git/issues/",
    },
    package_dir={'': 'semantic_git'},
    packages=find_packages(include=['semantic_git']),
    include_package_data=True,
    package_data={
        '': ['*.csv', '*.pk']
    },
    python_requires='>=3.6',
    install_requires=[
        'setuptools', 'colorama',
    ],
    scripts=['semantic_git/sgit_completer', 'semantic_git/sgit_bash_completer'],
    entry_points="""
    [console_scripts]
    sgit = sgit:main
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Environment :: Console',
    ],
)
