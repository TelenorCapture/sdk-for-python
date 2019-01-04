import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="target365-sdk",
    version="1.0.1",
    author="Target365",
    author_email="support@target365.no",
    description="Enables integration with Target365 online services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Target365/sdk-for-python",
    packages=setuptools.find_packages(),
    install_requires=[
          'requests',
          'ecdsa',
          'jsonpickle',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
