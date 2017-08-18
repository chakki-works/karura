from setuptools import setup, find_packages


requires = [
    "numpy>=1.13.1",
    "scipy>=0.19.1",
    "scikit-learn>=0.18.2",
    "matplotlib>=2.0.2",
    "pandas>=0.20.2"
]


setup(
    name="karura",
    version="0.1",
    description="karura enables you to use machine learning automatically & interactively",
    url="https://github.com/chakki-works/karura",
    author="icoxfog417",
    author_email="icoxfog417@yahoo.co.jp",
    license="Apache License 2.0",
    keywords="machine-learning kintone slackbot",
    packages=find_packages(exclude=["doc", "karura-kintone", "tests", "trained_models"]),
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)