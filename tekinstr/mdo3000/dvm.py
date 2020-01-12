"""Digital voltmeter (DVM) definition"""
from tekinstr.dvm import DVMBase


class DVM(DVMBase, kind="DVM"):
    """Digital voltmeter instrument

    Attributes:
        instr (Model)
        owner (Instrument)
        visa (pyvisa.resources.Resource): pyvisa resource
    """
