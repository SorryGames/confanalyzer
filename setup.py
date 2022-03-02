import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='confanalyzer',  
    version='0.2.1',
    data_files=[("", ["confanalyzer/template.html.jinja2"])],
    include_package_data=True,
    author="Solidex",
    author_email="info@solidex.by",
    description="Analyzer for configuration files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://git:3000/Solidex/confanalyzer",
    packages=setuptools.find_packages(),
    classifiers=[
     "Programming Language :: Python :: 3",
     "License :: OSI Approved :: MIT License",
     "Operating System :: OS Independent",
    ],
 )