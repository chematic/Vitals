import os
import sys
import time
import ctypes
import keyboard
import subprocess
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.prompt import Confirm
from rich.live import Live
from rich.text import Text
from core.engine import VitalsEngine
from core.logger import VitalsLogger

_c = Console()
VERSION = "1.2.0-PRO"
_rs = False

def isa():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def _dm():
    _p = " ".join([f'"{a}"' if " " in a else a for a in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, _p, None, 1)

def _f_gb(_v):
    return f"{_v / (1024**3):.2f} GB"

def create_dashboard(_d):
    if _rs:
        return Panel(
            Text("\n\n\nSYSTEM RESET IN PROGRESS\n\nRELOADING MODULES...", justify="center", style="bold yellow blink"),
            title="[b]RESET & PAUSE[/b]",
            border_style="yellow",
            expand=True
        )

    _l = Layout()
    _l.split_column(
        Layout(name="h", size=3),
        Layout(name="u", ratio=1),
        Layout(name="lo", ratio=1),
        Layout(name="f", size=3)
    )
    
    _c_d = _d['cpu']
    _ct = Table(expand=True, border_style="cyan", box=None, padding=(0,1))
    _ct.add_column("Property", style="bold cyan")
    _ct.add_column("Value", justify="right")
    _ct.add_row("Model", f"[white]{_c_d['brand']}[/white]")
    _ct.add_row("Usage Total", f"[bold green]{_c_d['usage_pct']}%[/bold green]")
    _ct.add_row("Temperature", f"[bold orange1]{_c_d['temp']}°C[/bold orange1]" if _c_d['temp'] else "N/A")
    _ct.add_row("Frequency", f"{_c_d['freq_current']} MHz")
    _ct.add_row("Power (Watt)", f"{_c_d.get('power', 'N/A')} W")
    _ct.add_row("Voltage", f"{_c_d.get('voltage', 'N/A')} V")

    _g_l = _d['gpu']
    _gt = Table(expand=True, border_style="yellow", box=None)
    if _g_l:
        _g = _g_l[0]
        _gt.add_row("Model", f"[white]{_g['name']}[/white]")
        _gt.add_row("Load", f"{_g['load']}%")
        _gt.add_row("Temp", f"{_g['temp']}°C")
        _gt.add_row("VRAM Used", f"{_f_gb(_g['mem_used'] * 1024**2)} / {_f_gb(_g['mem_total'] * 1024**2)}")
        _gt.add_row("Fan Speed", f"{_g.get('fan_speed', 'N/A')}%")
    else:
        _gt.add_row("Status", "No GPU Detected")

    _m_d = _d['memory']
    _st = Table(expand=True, border_style="magenta", box=None)
    _st.add_column("Device", style="bold magenta")
    _st.add_column("Used/Total", justify="right")
    _st.add_column("%", justify="right")
    
    _st.add_row("Physical RAM", f"{_f_gb(_m_d['ram_used'])} / {_f_gb(_m_d['ram_total'])}", f"{_m_d['ram_pct']}%")
    for _dk in _d['storage']:
        _st.add_row(f"Disk {_dk['device']}", f"{_f_gb(_dk['used'])} / {_f_gb(_dk['total'])}", f"{_dk['pct']}%")

    _f_s = _d.get('fans', [])
    _ft = Table(expand=True, border_style="green", box=None)
    _ft.add_column("Sensor", style="bold green")
    _ft.add_column("Speed", justify="right")
    if _f_s:
        for _fs in _f_s:
            _ft.add_row(_fs['name'], f"{int(_fs['value'])} RPM")
    else:
        _ft.add_row("Fans", "No sensors found")

    _up = datetime.fromtimestamp(_d['uptime']).strftime('%Y-%m-%d %H:%M:%S')
    _l["h"].update(Panel(f"[bold white]VITALS DOCKER[/bold white] | Uptime: {_up} | Time: {_d['timestamp']}", border_style="blue"))
    
    _l["u"].split_row(
        Layout(Panel(_ct, title="[b]PROCESSOR[/b]", border_style="cyan")),
        Layout(Panel(_gt, title="[b]GRAPHICS[/b]", border_style="yellow"))
    )
    _l["lo"].split_row(
        Layout(Panel(_st, title="[b]MEMORY & STORAGE[/b]", border_style="magenta")),
        Layout(Panel(_ft, title="[b]COOLING (FANS)[/b]", border_style="green"))
    )

    _l["f"].split_row(Layout(name="f_l"), Layout(name="f_m"), Layout(name="f_r"))
    _l["f_l"].update(Panel("[bold cyan]Q[/bold cyan] Exit | [bold cyan]L[/bold cyan] Log | [bold cyan]R[/bold cyan] Reset", border_style="white"))
    _l["f_m"].update(Panel(f"Health: [bold green]OPTIMAL[/bold green] | Admin: {isa()}", border_style="white"))
    _l["f_r"].update(Panel(f"Vitals Engine v{VERSION} | [bold yellow]AMD-SMU[/bold yellow]", border_style="white"))
    
    return _l

def main():
    global _rs
    _bp = os.path.dirname(os.path.abspath(__file__))
    _ld = os.path.join(_bp, "logs")
    _lg = VitalsLogger(_ld)

    _lg.log("-- LOGS --")
    _lg.log(f"Version: {VERSION}")
    _lg.log(f"Admin Status: {isa()}")

    if not isa():
        _lg.log("Admin privileges required. Prompting user...")
        if Confirm.ask("[bold yellow]Relaunch as Admin?[/bold yellow]", default=True):
            _lg.log("Attempting elevation...")
            _dm()
            sys.exit(0)
        _lg.log("Elevation refused. Exiting.", "ERROR")
        sys.exit(1)

    _lg.log("Initializing Engine...")
    _en = VitalsEngine()

    def _o_l():
        _lg.log("Hotkey 'L' detected: Opening logs")
        _lf = os.path.join(_ld, "vitals_runtime.log")
        if os.path.exists(_lf): 
            try:
                subprocess.Popen(['notepad.exe', _lf])
                _lg.log(f"Notepad spawned for {_lf}")
            except Exception as _e:
                _lg.log(f"Failed to open log: {_e}", "ERROR")

    def _r_e():
        global _rs
        _lg.log("Hotkey 'R' detected: Resetting...")
        _rs = True
        time.sleep(2)
        _px = sys.executable
        _sp = sys.argv[0]
        _lg.log(f"Relaunching: {_px} {_sp}")
        os.execv(_px, [f'"{_px}"', f'"{_sp}"'] + sys.argv[1:])

    keyboard.add_hotkey('q', lambda: (_lg.log("Hotkey 'Q' detected: Exiting"), os._exit(0)))
    keyboard.add_hotkey('l', _o_l)
    keyboard.add_hotkey('r', _r_e)
    _lg.log("Hotkeys registered")

    _lg.log("Starting Live UI loop")
    try:
        with Live(screen=True, auto_refresh=True, refresh_per_second=2) as _lv:
            while True:
                if not _rs:
                    _rd = _en.get_system_vitals()
                    _rd['timestamp'] = datetime.now().strftime("%H:%M:%S")
                    _lv.update(create_dashboard(_rd))
                else:
                    _lv.update(create_dashboard(None))
                time.sleep(0.5)
    except Exception as _e:
        _lg.log(f"Critical Loop Error: {_e}", "ERROR")

if __name__ == "__main__":
    main()