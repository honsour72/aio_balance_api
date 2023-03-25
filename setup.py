from setuptools import setup


setup(
    name="app",
    version='0.0.1',
    author="Rogozin",
    author_email="honsour72@gmail.com",
    packages=['app'],
    install_requires=open("./requirements/base.txt").read().splitlines(),
    # setup_requires=open("requirements/dev.txt").read().splitlines(),
    python_requires='>3',
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="http://m-rogozin,ru",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'run_app=app.__main__:main'
        ]
    },
)
