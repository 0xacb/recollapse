from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="recollapse",
    version="1.0.0",
    author="0xacb",
    author_email="",
    description="REcollapse is a helper tool for black-box regex fuzzing to bypass validations and discover normalizations in web applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0xacb/recollapse",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "recollapse=recollapse.cli:main",
        ],
    },
    keywords="security, fuzzing, regex, bypass, normalization, waf",
    project_urls={
        "Bug Reports": "https://github.com/0xacb/recollapse/issues",
        "Source": "https://github.com/0xacb/recollapse",
        "Documentation": "https://github.com/0xacb/recollapse#readme",
    },
)