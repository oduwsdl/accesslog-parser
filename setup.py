import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="accesslog",
    version="0.1.0b2",
    author="Sawood Alam",
    author_email="ibnesayeed@gmail.com",
    description="Web server access log parser and CLI tool with added features for web archive replay logs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oduwsdl/archive-accesslog",
    license="MIT License",
    packages=setuptools.find_packages(),
    provides=[
        "accesslog"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: Log Analysis"
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "accesslog = accesslog.__main__:main"
        ]
    }
)
