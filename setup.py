import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="infoicer", # Replace with your own username
    version="0.0.1",
    license='MIT',
    author="Eden Kirin",
    author_email="edkirin@gmail.com",
    description="Infoicer is a simple invoice items handler.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edkirin/infoicer",
    keywords=['invoice'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
