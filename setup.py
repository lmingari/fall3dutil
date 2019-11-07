import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fall3d-metpy", 
    version="1.0",
    author="Leonardo Mingari",
    author_email="lmingari@gmail.com",
    description="Met utilities for the FALL3D model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lmingari/fall3d-metpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
