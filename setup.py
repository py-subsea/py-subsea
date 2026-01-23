from setuptools import setup, find_packages

setup(
    name="pysubsea",
    version="0.1.1",
    description="Package for subsea pipelines and risers design in Python",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/py-subsea/py-subsea",
    author="ismael-ripoll",
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[],
    project_urls={
        "Documentation": "https://py-subsea.github.io/py-subsea/",
        "Source": "https://github.com/py-subsea/py-subsea",
        "Tracker": "https://github.com/py-subsea/py-subsea/issues",
    }
)