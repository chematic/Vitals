# c.py
import psutil
import cpuinfo
class CPULogic:
    def __init__(self, _h, _ch, _lg):
        self._h = _h
        self._ch = _ch
        self._lg = _lg
        self._cb = None

    def _g_v(self):
        _v = {"temp": None, "power": "N/A", "voltage": "N/A"}
        if not self._ch: return _v
        try:
            self._ch.Update()
            for _s in self._ch.Sensors:
                _st = _s.SensorType.ToString()
                _sn = _s.Name
                _sv = _s.Value
                if _sv is None: continue
                if _st == "Temperature":
                    if "Tctl" in _sn or "Package" in _sn:
                        if _sv > 0 and _v["temp"] is None:
                            _v["temp"] = round(float(_sv), 1)
                elif _st == "Power" and "Package" in _sn:
                    _v["power"] = round(float(_sv), 1)
                elif _st == "Voltage" and ("VCore" in _sn or "CPU Core" in _sn):
                    _v["voltage"] = round(float(_sv), 3)
            if _v["temp"] is None:
                for _s in self._ch.Sensors:
                    if _s.SensorType.ToString() == "Temperature" and _s.Value > 1.0:
                        _v["temp"] = round(float(_s.Value), 1)
                        break
        except Exception as _e:
            self._lg.log(f"C_ERR: {_e}", "ERROR")
        return _v

    def _f_a(self):
        try:
            if not self._cb:
                self._cb = cpuinfo.get_cpu_info().get('brand_raw', "AMD Ryzen")
        except: self._cb = "AMD Ryzen 5 5600X"
        _vi = self._g_v()
        return {
            "brand": self._cb,
            "usage_pct": psutil.cpu_percent(interval=None),
            "freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "temp": _vi["temp"],
            "power": _vi["power"],
            "voltage": _vi["voltage"],
            "cores_phys": psutil.cpu_count(logical=False),
            "cores_log": psutil.cpu_count(logical=True)
        }