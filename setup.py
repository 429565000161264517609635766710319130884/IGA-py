import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
fh.close()

setuptools.setup(
    name="IGA_py",
    version="1.0.0",
    author="Quatrecentquatre-404",
    author_email="obvious.ly.dev@gmail.com",
    description="Here is an Instagram Guest API. Gather all public information as JSON format without logging yourself. It's all automation and time saving.",
    long_description=long_description,
    url="https://github.com/Quatrecentquatre-404/IGA-py",
    license="LICENSE",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
    packages=["src"],
)
