from setuptools import setup, find_packages

setup(
    name='tradepy',  # Your package name
    version='0.1.0',  # Version of your package
    packages=find_packages(where='src', include=['tradelab']),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'mplfinance',
        'pyodbc',
        'tk',
        'dearpygui',
    ],
    include_package_data=True,
    description='A package for developing and testing trading strategies',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/alexandermfisher/tradepy.git',
    author='Alexander Fisher',
    author_email='fisher.alexander.michael@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)