# g.py
import GPUtil
class GPULogic:
    def _g_a(self):
        _gd = []
        try:
            for _g in GPUtil.getGPUs():
                _gd.append({
                    "name": _g.name,
                    "load": _g.load * 100,
                    "temp": _g.temperature,
                    "mem_used": _g.memoryUsed,
                    "mem_total": _g.memoryTotal
                })
        except: pass
        return _gd