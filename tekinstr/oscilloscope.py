"""Oscilloscope base class"""
import re
from datetime import datetime, timedelta
import sys
import asyncio
import itertools
from dataclasses import dataclass
import numpy as np
import pyvisa
from tekinstr.instrument import Instrument, InstrumentSubsystem
from tekinstr.common import validate
from waveformDT.waveform import WaveformDT


@dataclass
class State:
    """Signal for controlling asyncio tasks"""

    running: bool = False


class OscilloscopeBase(Instrument, kind="OscilloscopeBase"):
    """Oscilloscope base class

    Attributes:
        instr (Model)
    """

    def __init__(self, instr):
        super().__init__(instr)
        self._state = State()

    @property
    def horizontal_scale(self):
        """value (float): amount of time per division coerced to nearest setting"""
        return float(self._visa.query("HORIZONTAL:SCALE?"))

    @horizontal_scale.setter
    @validate
    def horizontal_scale(self, value):
        self._visa.write(f"HORIZONTAL:SCALE {float(value)}")

    @property
    def horizontal_delay_mode(self):
        """value (str): delay_time or pretrigger_percent
            delay_time: center waveform horizontal_position seconds after trigger occurs
            pretrigger_percent: horizontal_position percent of record length
        """
        mode = self._visa.query("HORIZONTAL:DELAY:STATE?")
        return "delay_time" if mode in ["ON", "1"] else "pretrigger_percent"

    @horizontal_delay_mode.setter
    @validate
    def horizontal_delay_mode(self, value):
        mode = "ON" if value == "delay_time" else "OFF"
        self._visa.write(f"HORIZONTAL:DELAY:STATE {mode}")

    @property
    def horizontal_position(self):
        """value (float): position of waveform on display based on horizontal_delay_mode
            delay_time: center waveform horizontal_position seconds after trigger occurs
            pretrigger_percent: horizontal_position percent of record length
        """
        delay_time = float(self._visa.query("HORIZONTAL:DELAY:TIME?"))
        pretrigger_percent = float(self._visa.query("HORIZONTAL:TRIGGER:POSITION?"))
        if self.horizontal_delay_mode in ["0", "OFF"]:
            horizontal_position = pretrigger_percent
        else:
            horizontal_position = delay_time
        return horizontal_position

    @horizontal_position.setter
    @validate
    def horizontal_position(self, value):
        if self.horizontal_delay_mode in ["0", "OFF"]:
            self._visa.write(f"HORIZONTAL:TRIGGER:POSITION {float(value)}")
        else:
            self._visa.write(f"HORIZONTAL:DELAY:TIME {float(value)}")

    @property
    def record_length(self):
        """value (int): 500 or 10000 samples"""
        return int(self._visa.query("HORIZONTAL:RECORDLENGTH?"))

    @record_length.setter
    @validate
    def record_length(self, value):
        self._visa.write(f"HORIZONTAL:RECORDLENGTH {int(value)}")

    @property
    def acquisition_mode(self):
        """value (str): acquisition mode; SAMPLE, PEAKDETECT, AVERAGE, ENVELOPE
            AVERAGE - specify num_averages
            ENVELOPE - specify num_envelopes
        """
        return self._visa.query("ACQUIRE:MODE?")

    @acquisition_mode.setter
    @validate
    def acquisition_mode(self, value):
        self._visa.write(f"ACQUIRE:MODE {value}")

    @property
    def acquisition_count(self):
        """(int): number of acquisitions since setting acquisition_state to RUN

            This value is reset to zero when any acquisition, horizontal or vertical
            arguments that affect the waveform are changed.
        """
        return int(self._visa.query("ACQUIRE:NUMACQ?"))

    @property
    def num_averages(self):
        """value (int): number of waveforms to average
            The range of values is 2 to 512 in powers of 2.
        """
        return int(self._visa.query("ACQUIRE:NUMAVG?"))

    @num_averages.setter
    @validate
    def num_averages(self, value):
        self._visa.write(f"ACQUIRE:NUMAVG {value}")

    @property
    def num_envelopes(self):
        """value (int or str): number of envelopes from 1 to 2000 or INFINITE"""
        return self._visa.query("ACQUIRE:NUMENV?")

    @num_envelopes.setter
    @validate
    def num_envelopes(self, value):
        self._visa.write(f"ACQUIRE:NUMENV {value}")

    @property
    def acquisition_state(self):
        """value (str): start or stop acquisition; RUN (1) or STOP (0)"""
        return self._visa.query("ACQUIRE:STATE?")

    @acquisition_state.setter
    @validate
    def acquisition_state(self, value):
        self._visa.write(f"ACQUIRE:STATE {value}")

    @property
    def single_acquisition(self):
        """value (bool): single or continuous acquisitions
            For single acqusitions set to True
            For continuous acquisitions set to False
        """
        stop_after = self._visa.query("ACQUIRE:STOPAFTER?")
        return stop_after == "SEQUENCE"

    @single_acquisition.setter
    @validate
    def single_acquisition(self, value):
        stop_after = "SEQUENCE" if value else "RUNSTOP"
        self._visa.write(f"ACQUIRE:STOPAFTER {stop_after}")
        stop_after = self._visa.query("ACQUIRE:STOPAFTER?")

    def _get_wfmpre(self, inout=""):
        """Get waveform preamble

        Args:
            inout (str): IN, OUT or '' depending on model and signal direction
        """
        self._visa.write("HEADER ON")
        pre_str = self._visa.query(f"WFM{inout}PRE?").replace(f":WFM{inout}PRE:", "")
        raw_preamble = dict([kv.split(" ", maxsplit=1) for kv in pre_str.split(";")])
        preamble = {}
        for k, v in raw_preamble.items():
            value = v.strip('"')
            try:
                value = int(v)
            except ValueError:
                try:
                    value = float(v)
                except ValueError:
                    pass
            preamble[k] = value
        self._visa.write("HEADER OFF")
        return preamble

    async def _show_spinner(self):
        """Show an in-progress spinner during acquisition"""
        spinner = itertools.cycle(["-", "/", "|", "\\"])
        try:
            while self._state.running:
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                sys.stdout.write("\b")
                await asyncio.sleep(0.5)
            return 0
        except asyncio.CancelledError:
            pass
        finally:
            sys.stdout.write("\b \b")

    async def _acquire(self):
        """Acquire single sequence"""
        try:
            self._visa.write("*SRE 32")
            self._visa.write("*ESE 61")
            self._visa.write("*CLS")
            original_sa = self.single_acquisition
            self.single_acquisition = True
            self._visa.write(f"ACQUIRE:STATE RUN; *OPC")
            # poll the ESB bit for an event occurance indicating completion or error
            while not self._visa.stb & 32:
                await asyncio.sleep(1)
            esr = int(self._visa.query("*ESR?"))
            op_complete = bool(esr & 1)
            self.single_acquisition = original_sa
            return 0 if op_complete else 1
        except asyncio.CancelledError:
            pass
        except pyvisa.VisaIOError as exc:
            if exc.abbreviation == "VI_ERROR_TMO":
                raise TimeoutError(
                    "Acquisition timed out due to loss of communication"
                ) from None
            else:
                raise
        finally:
            self._state.running = False

    async def _start_task(self, timeout):
        """timeout (int): timeout in seconds"""
        self._state.running = True
        task = asyncio.gather(self._show_spinner(), self._acquire())
        try:
            ret_value = await asyncio.wait_for(task, timeout)
        except asyncio.TimeoutError:
            task.exception()  # retrieve the _GatheringFuture exception
            raise TimeoutError(
                "Acquisition didn't complete before specified timeout value"
            ) from None
        else:
            return ret_value

    def read(self, channels, samples="all", timeout=10, wdt=True, previous=True):
        """Transfer waveform data of the specified channel(s) from the oscilloscope

        Args:
            channels (str): specification such as 'CH1', 'CH1:4', or ['CH1', 'CH2']
                Acquisition is temporarily stopped to ensure all channel data come from
                the same acquisition instance.
            samples ('all', int or tuple): If 'all', return record_length samples.
                If an integer, return N samples starting with the
                first sample in the record. If a tuple (start, stop), return
                samples start to stop from the record.
            timeout (float): timeout, in seconds, only has meaning when previous
                is set to False, otherwise return the latest acquired waveform. A value
                of None means no timeout.
            wdt (bool): If true, return data as WaveformDT.
            previous (bool): If True, just read the existing waveform data. If False,
                initiate a new single sequence.
        Returns:
            WaveformDT or numpy.ndarray
        """
        chs = []
        if isinstance(channels, str):
            match = re.match("^CH(?P<first>[1-4])(?P<last>:[1-4])?$", channels)
            if match is None:
                raise ValueError(f"{channels} not a valid specification")
            first = int(match.group("first"))
            last = match.group("last")
            if last is None:
                last = first
            else:
                last = int(last[-1])
            for ch in range(first, last + 1):
                chs.append(f"CH{ch}")
            channels = chs
        if isinstance(samples, tuple):
            start, stop = samples
        elif isinstance(samples, int):
            start = 1
            stop = samples
        else:
            start = 1
            stop = self.record_length
        self._visa.write(f"DATA:START {start}")
        self._visa.write(f"DATA:STOP {stop}")
        self._visa.write("DATA:WIDTH 1")
        self._visa.write("DATA:ENCDG RIBinary")
        original_state = self.acquisition_state
        self._visa.write("ACQUIRE:STATE STOP")
        if not previous:
            ret_value = asyncio.run(self._start_task(timeout))
            if ret_value is None:
                return None
            if ret_value[1] > 0:
                print(self._instr.status.event_status)
                return None
        time = self._visa.query("TIME?")
        date = self._visa.query("DATE?")
        data = []
        for channel in channels:
            self._visa.write(f"DATA:SOURCE {channel}")
            preamble = self._get_wfmpre()
            y_offset = preamble["YZERO"]  # in y_unit
            y_multiplier = preamble[
                "YMULT"
            ]  # conversion from data point level to y_unit
            y_position = preamble["YOFF"]  # in data point levels
            rawdata = self._visa.query_binary_values(
                "CURVE?", "b", container=np.ndarray
            )
            data.append(y_offset + y_multiplier * (rawdata - y_position))
        self.acquisition_state = original_state
        data = data[0] if len(data) == 1 else np.asarray(data)
        if wdt:
            time = [int(n) for n in time.strip().strip('"').split(":")]
            date = [int(n) for n in date.strip().strip('"').split("-")]
            t0 = datetime(*date, *time) + timedelta(seconds=preamble["XZERO"])
            dt = preamble["XINCR"]
            data = WaveformDT(data, dt, t0)
            setattr(data, "wf_start_offset", preamble["XZERO"])
            setattr(data, "_xunit", preamble["XUNIT"])
            setattr(data, "_yunit", preamble["YUNIT"])
            setattr(data, "y_position", y_position * y_multiplier)
            setattr(data, "y_offset", y_offset)
        return data

    def force_trigger(self):
        """Force a trigger event"""
        self._visa.write("TRIGGER FORCE")

    @property
    def trigger_state(self):
        """(str): ARMED, AUTO, READY, SAVE, TRIGGER"""
        return self._visa.query("TRIGGER:STATE?")


class ChannelBase(InstrumentSubsystem, kind="ChannelBase"):
    """Oscilloscope channel

    Attributes:
        owner (Instrument)
        CHx (int): channel number
    """

    def __init__(self, owner, CHx):
        super().__init__(owner)
        self._ch = CHx

    @property
    def bandwidth(self):
        """value (str): TWENTY, ONEFIFTY or FULL"""
        return self._visa.query(f"CH{self._ch}:BANDWIDTH?")

    @bandwidth.setter
    def bandwidth(self, value):
        self._visa.write(f"CH{self._ch}:BANDWIDTH {value}")

    @property
    def coupling(self):
        """value (str): AC, DC or GND"""
        return self._visa.query(f"CH{self._ch}:COUPLING?")

    @coupling.setter
    def coupling(self, value):
        self._visa.write(f"CH{self._ch}:COUPLING {value}")

    @property
    def invert(self):
        """value (str): ON (1) or OFF (0)"""
        return self._visa.query(f"CH{self._ch}:INVERT?")

    @invert.setter
    def invert(self, value):
        self._visa.write(f"CH{self._ch}:INVERT {value}")

    @property
    def offset(self):
        """value (float): value subtracted from the signal before acquisition"""
        return float(self._visa.query(f"CH{self._ch}:OFFSET?"))

    @offset.setter
    def offset(self, value):
        self._visa.write(f"CH{self._ch}:OFFSET {value}")

    @property
    def position(self):
        """value (float): vertical position in divisions from center graticule"""
        return float(self._visa.query(f"CH{self._ch}:POSITION?"))

    @position.setter
    def position(self, value):
        self._visa.write(f"CH{self._ch}:POSITION {value}")

    @property
    def scale(self):
        """value (float): vertical gain in y_unit per division"""
        return float(self._visa.query(f"CH{self._ch}:SCALE?"))

    @scale.setter
    def scale(self, value):
        self._visa.write(f"CH{self._ch}:SCALE {value}")

    @property
    def y_unit(self):
        """value (str): 'V' for voltage or 'A' for amperage"""
        return self._visa.query(f"CH{self._ch}:YUN?").strip('"')

    @y_unit.setter
    def y_unit(self, value):
        self._visa.write(f"CH{self._ch}:YUN '{value}'")


class ProbeBase(InstrumentSubsystem, kind="ProbeBase"):
    """Oscilloscope channel

    Attributes:
        owner (InstrumentSubsystem)
    """

    def __init__(self, owner):
        super().__init__(owner)
        self._ch = owner._ch

    @property
    def model(self):
        """(str): probe model"""
        return self._visa.query(f"CH{self._ch}:ID?").strip('"')

    @property
    def gain(self):
        """value (float): probe gain factor (output/input)"""
        return float(self._visa.query(f"CH{self._ch}:PROBE?"))

    @gain.setter
    @validate
    def gain(self, value):
        self._visa.write(f"CH{self._ch}:PROBE {value}")

    @property
    def impedance(self):
        """value (float): probe impedance in ohms"""
        impedance = self._visa.query(f"CH{self._ch}:IMPEDANCE?")
        if impedance == "MEG":
            impedance = 1e6
        elif impedance == "FIFTY":
            impedance = 50.0
        return impedance

    def __repr__(self):
        instr_model = self._instr.model
        instr = self._owner._owner._kind
        subsys = self._owner._kind
        return f"<{instr_model} {instr} {subsys} {self._kind} {self.model}>"
