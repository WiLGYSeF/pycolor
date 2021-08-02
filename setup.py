import setuptools

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

with open('requirements.txt', 'r', encoding='utf-8') as file:
    install_requires = file.read().split('\n')

setuptools.setup(
    name='pycolor-term',
    version='0.0.5',
    author='wilgysef',
    author_email='wilgysef@gmail.com',
    description='Execute commands to perform real-time terminal output coloring using ANSI color codes.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/WiLGYSeF/pycolor',
    project_urls={
        'Bug Tracker': 'https://github.com/WiLGYSeF/pycolor/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires,
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['pycolor=pycolor.__main__:main_args']
    }
)
