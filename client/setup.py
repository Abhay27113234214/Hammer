from setuptools import setup

setup(
    name="hammer",
    version="0.1.0",
    py_modules=["cli"], 
    install_requires=[
        "typer",
    ],
    entry_points={
        "console_scripts": [
            "hammer=cli:main", 
        ],
    },
)