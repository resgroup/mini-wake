import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="miniwake",
    version="0.0.4",
    author="RES",
    author_email="software.team@res-group.com",
    description="An open-source, light weight, fast to run, easy to understand & carefully crafted implementation of the Ainslie eddy viscosity wake model and associated sub-models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/resgroup/mini-wake",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["numpy==1.*", "scipy==1.*"],
)
