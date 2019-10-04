import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='sequdas_qc',
    version='1.0.0',
    description='Sequence Upload and Data Archiving System',
    url='https://github.com/duanjunhyq/sequdas_qc',
    author='Jun Duan',
    author_email='jun.duan@bccdc.ca',
    long_description=long_description,
    long_description_content_type="text/markdown",
    licence='MIT',
    keywords="NGS sequence archive analysis",    
    packages=setuptools.find_packages(include=['sequdas_qc','sequdas_qc.Lib']),
    install_requires=['configparser','mysql-connector-python','pytz','ntplib','validate_email'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data = True,
    python_requires='>=3.6',
    entry_points={
    	'console_scripts': [
    		'sequdas-qc=sequdas_qc.sequdas_qc:main'
    	]
    },
  
)
