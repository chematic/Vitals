import psutil
import os
import clr
import sys
import time
import ctypes
from core.logger import VitalsLogger
from core.providers.c import CPULogic
from core.providers.g import GPULogic
from core.providers.m import MEMLogic
from core.providers.s import STOLogic

class VitalsEngine:
    def __init__(self):
        _bp = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _lp = os.path.join(_bp, "logs")
        self.logger = VitalsLogger(_lp)
        self.logger.log("Engine Init: Step 1 - Privilege elevation")
        self._e_p_p()
        self._bd = os.path.join(_bp, "bin")
        self._md = os.path.join(self._bd, "LibreHardwareMonitorLib.dll")
        self.logger.log(f"Engine Init: Step 2 - Path check: {self._md}")
        self._h = None
        self._ch = None
        self._bt = psutil.boot_time()
        try:
            self.logger.log("Engine Init: Step 3 - Appending sys.path")
            if self._bd not in sys.path: sys.path.append(self._bd)
            self.logger.log("Engine Init: Step 4 - Adding CLR Reference")
            clr.AddReference("LibreHardwareMonitorLib")
            from LibreHardwareMonitor.Hardware import Computer
            self.logger.log("Engine Init: Step 5 - Instantiating Computer object")
            self._h = Computer()
            self._h.IsCpuEnabled = True
            self._h.IsGpuEnabled = False 
            self.logger.log("Engine Init: Step 6 - Opening Handle")
            self._h.Open()
            self.logger.log("Engine Init: Step 7 - Ring 0 driver sync (1.0s)")
            time.sleep(1.0) 
            self.logger.log("Engine Init: Step 8 - Locating CPU hardware")
            for _hw in self._h.Hardware:
                if _hw.HardwareType.ToString() == "Cpu":
                    self._ch = _hw
                    self.logger.log("Engine Init: Step 9 - AMD SMU Triple Update")
                    self._ch.Update()
                    time.sleep(0.1)
                    self._ch.Update()
            self._p_c = CPULogic(self._h, self._ch, self.logger)
            self._p_g = GPULogic()
            self._p_m = MEMLogic()
            self._p_s = STOLogic()
            self.logger.log("Engine initialized in High Performance mode.")
        except Exception as _e:
            self.logger.log(f"Init Error: {str(_e)}", "ERROR")

    def _e_p_p(self):
        try:
            _p = psutil.Process(os.getpid())
            _p.nice(psutil.REALTIME_PRIORITY_CLASS)
            _a32 = ctypes.windll.advapi32
            _ht = ctypes.c_void_p()
            if _a32.OpenProcessToken(ctypes.windll.kernel32.GetCurrentProcess(), 0x0020 | 0x0008, ctypes.byref(_ht)):
                _li = ctypes.c_longlong()
                if _a32.LookupPrivilegeValueW(None, "SeDebugPrivilege", ctypes.byref(_li)):
                    class L_A_A(ctypes.Structure):
                        _fields_ = [("Luid", ctypes.c_longlong), ("Attributes", ctypes.c_uint32)]
                    class T_P(ctypes.Structure):
                        _fields_ = [("PrivilegeCount", ctypes.c_uint32), ("Privileges", L_A_A)]
                    _tp = T_P(1, L_A_A(_li.value, 0x00000002))
                    _a32.AdjustTokenPrivileges(_ht, False, ctypes.byref(_tp), 0, None, None)
                    self.logger.log("SeDebugPrivilege enabled")
        except Exception as _e: self.logger.log(f"Elevation bypass: {_e}", "WARNING")

    def get_system_vitals(self):
        return {
            "cpu": self._p_c._f_a(),
            "gpu": self._p_g._g_a(),
            "memory": self._p_m._g_m(),
            "storage": self._p_s._g_s(),
            "uptime": self._bt
        }