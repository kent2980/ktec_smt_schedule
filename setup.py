from setuptools import setup, find_packages

setup(
    name="ktec_smt_schedule",
    version="0.1.0",
    description="SMT Schedule processing library",
    packages=["ktec_smt_schedule"],
    package_dir={"ktec_smt_schedule": "src"},
    install_requires=[
        "cookiecutter>=2.6.0",
        "openpyxl>=3.1.5",
        "pandas>=2.3.3",
        "pytest>=8.4.2",
        "pyxlsb>=1.0.10",
        "setuptools>=80.9.0",
        "styleframe>=4.2",
        "wheel>=0.45.1",
        "xlrd>=2.0.2",
    ],
    python_requires=">=3.12",
)
