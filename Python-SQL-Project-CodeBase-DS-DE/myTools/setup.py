import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="myTools-scorniglion",
    version="0.0.1",
    author="Sébastien Corniglion",
    author_email="sebastien.corniglion@dsti.institute",
    description="myTools offers utility classes and functions for dealing with the DSTI combined SQL & Python project",
    url="",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)

