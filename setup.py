"""Setuptools install script"""
from setuptools import setup

setup(
    name="tekinstr",
    version="0.0.0",
    author="Lee Johnston",
    author_email="lee.johnston.100@gmail.com",
    description="Communication with Tektronix oscilloscopes",
    packages=["tekinstr"],
    license="MIT",
    install_requires=["numpy", "sympy", "unit_system", "pyvisa"],
)
