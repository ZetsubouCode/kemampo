import kemampo

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kemampo", # Replace with your own username
    version=str(kemampo.__version__),
    author="Erlangga Ibrahim",
    author_email="erlanggaibr2@gmail.com",
    description="A handy, small, library to cut down SQLAlchemy builerplates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dolano-tours/kemampo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
