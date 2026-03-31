# m.py
import psutil
class MEMLogic:
    def _g_m(self):
        _m = psutil.virtual_memory()
        return {"ram_total": _m.total, "ram_used": _m.used, "ram_pct": _m.percent}
