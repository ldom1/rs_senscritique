from setuptools import setup, find_packages

install_requires = [
    "surprise",
    "numpy",
    "pandas",
    "scikit-learn",
    "tqdm",
    "user_agent",
    "bs4",
    "requests",
    "lxml",
    "streamlit",
    "unidecode",
]

dev_requires = [
    "autopep8",
    "pytest",
    "pytest-cov",
    "mock",
    "pytest-mock",
    "pytest-timeout",
    "twine",
    "coverage-badge",
    "semver",
    "flake8",
    "pylint",
    "moto"
]
setup(
    name='rssenscritique',
    version="1.0.0",
    description='recommend you movies',
    author='Louis Giron',
    license='',
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
    include_package_data=True,
    extras_require={"dev": dev_requires}
)
