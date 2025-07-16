from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gabiteodoru-qython",
    version="0.1.0",
    author="Gabi Teodoru",
    author_email="gabiteodoru@gmail.com",
    description="Qython: Python-like syntax with q-functional constructs translator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gabiteodoru/qython",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.8",
    install_requires=[
        "parso",
    ],
    package_data={
        "qython": ["custom_grammar.txt"],
    },
    keywords="q kdb qython compiler translator functional-programming",
)