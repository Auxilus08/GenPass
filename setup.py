from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="genpass",
    version="1.0.0",
    author="Akshat Tiwari",
    description="A secure password manager with 2FA support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akshat0824/GenPass",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'genpass=src.main:main',
        ],
    },
)