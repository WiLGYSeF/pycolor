import setuptools

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setuptools.setup(
    name='pycolor-term',
    version='0.0.8',
    author='wilgysef',
    author_email='wilgysef@gmail.com',
    description='Execute commands, coloring terminal output in real-time using ANSI color codes.',
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
    install_requires=['fastjsonschema'],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    include_package_data=True,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['pycolor=pycolor.__main__:main_args']
    }
)
