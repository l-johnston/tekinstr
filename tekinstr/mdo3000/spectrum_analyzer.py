"""Spectrum analyzer instrument definition"""
from tekinstr.spectrum_analyzer import SpectrumAnalyzerBase


class SpectrumAnalyzer(SpectrumAnalyzerBase, kind="Spectrum Analyzer"):
    """Spectrum analyzer instrument

    Attributes:
        instr (Model)
        visa (pyvisa.resources.Resource): pyvisa resource
    """
