import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fall3dutil", 
    version="1.2",
    author="Leonardo Mingari",
    author_email="lmingari@gmail.com",
    description="Utilities for the FALL3D model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lmingari/fall3dutil",
    packages=setuptools.find_packages(),
    install_requires=[
        'cdsapi',
        'netcdf4',
        'configparser',
        'numpy',
        'requests',
        'datetime',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
