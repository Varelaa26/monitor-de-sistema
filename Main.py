import os
import shutil
import subprocess
import sys

import customtkinter as ctk
import psutil as ps


def _system_disk_root() -> str:
    drive = os.path.splitdrive(os.path.abspath(os.sep))[0]
    if drive:
        return drive + os.sep
    return os.sep


def _gpu_utilizacao_nvidia_percent() -> float | None:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return None
    try:
        run_kw: dict = {
            "capture_output": True,
            "text": True,
            "timeout": 5,
        }
        if sys.platform == "win32":
            run_kw["creationflags"] = subprocess.CREATE_NO_WINDOW
        completed = subprocess.run(
            [
                exe,
                "--query-gpu=utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            **run_kw,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    linha = (completed.stdout or "").strip().splitlines()
    if not linha:
        return None
    try:
        return float(linha[0].strip())
    except ValueError:
        return None


class Main(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self._disk_root = _system_disk_root()

        self.title("Monitor do sistema")
        self.geometry("440x320")

        self._build_layout()
        self.after(100, self._update_metrics)
        self._present_window()

    def _build_layout(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="Monitor do sistema",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(pady=(20, 16))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self._cpu_label = ctk.CTkLabel(
            body,
            text="CPU: —",
            font=ctk.CTkFont(size=16),
            anchor="w",
        )
        self._cpu_label.pack(fill="x", pady=6)

        self._ram_label = ctk.CTkLabel(
            body,
            text="RAM: —",
            font=ctk.CTkFont(size=16),
            anchor="w",
        )
        self._ram_label.pack(fill="x", pady=6)

        self._gpu_label = ctk.CTkLabel(
            body,
            text="GPU: —",
            font=ctk.CTkFont(size=16),
            anchor="w",
        )
        self._gpu_label.pack(fill="x", pady=6)

        self._storage_label = ctk.CTkLabel(
            body,
            text="Armazenamento: —",
            font=ctk.CTkFont(size=16),
            anchor="w",
        )
        self._storage_label.pack(fill="x", pady=6)

    def _present_window(self) -> None:
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(250, lambda: self.attributes("-topmost", False))
        if sys.platform == "win32":
            self.focus_force()

    def _update_metrics(self) -> None:
        try:
            cpu = ps.cpu_percent(interval=0.1)
            ram = ps.virtual_memory().percent
            disk = ps.disk_usage(self._disk_root).percent
            self._cpu_label.configure(text=f"CPU: {cpu:.1f}%")
            self._ram_label.configure(text=f"RAM: {ram:.1f}%")
            gpu_pct = _gpu_utilizacao_nvidia_percent()
            if gpu_pct is not None:
                self._gpu_label.configure(text=f"GPU: {gpu_pct:.1f}%")
            else:
                self._gpu_label.configure(text="GPU: Sem informações")
            self._storage_label.configure(text=f"Armazenamento: {disk:.1f}%")
        except OSError as exc:
            self._cpu_label.configure(text=f"Erro ao ler métricas: {exc}")

        self.after(1500, self._update_metrics)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = Main()
    app.mainloop()
