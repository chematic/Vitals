# s.py
import psutil
class STOLogic:
    def _g_s(self):
        _ds = []
        for _p in psutil.disk_partitions(all=False):
            if 'fixed' in _p.opts:
                try:
                    _u = psutil.disk_usage(_p.mountpoint)
                    _ds.append({"device": _p.device, "total": _u.total, "used": _u.used, "pct": _u.percent})
                except: continue
        return _ds