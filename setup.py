from setuptools import find_packages, setup

setup(
    name="redact_app",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "redact = redact.main:main",
        ],
    },
    install_requires=[
        # Add required dependencies here
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for redacting and unredacting files",
    license="MIT",
    keywords="redact unredact",
    url="https://github.com/your_username/redact_app",
)
