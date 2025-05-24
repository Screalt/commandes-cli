# setup.py
from setuptools import setup, find_packages

setup(
    name="commandes-cli",
    version="0.1.0",
    description="Client CLI pour récupérer et imprimer des commandes par e-mail",
    author="Screalt",
    url="https://github.com/Screalt/commandes-cli",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "pycups",
    ],
    entry_points={
        "console_scripts": [
            "commandes-cli=commandes_cli.cli:cli_menu",
        ]
    },
)
