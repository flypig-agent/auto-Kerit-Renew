import os
import json
import tempfile
import subprocess
import time
import shutil
from urllib.parse import urlparse, parse_qs, unquote

class SingboxRunner:
    """Simple sing-box runner that generates a minimal config from a NODE_LINK-like
    node string and starts the sing-box process, exposing a local socks5 proxy.

    Notes:
    - This script assumes `sing-box` (or `sing-box` binary on PATH) is installed on the host.
    - It writes a temporary config JSON and launches `sing-box run -c <config>` (binary name may be `sing-box`).
    - The generated config is intentionally minimal and may need adjustments for some link types.
    """

    def __init__(self, node_link: str, listen_addr: str = "127.0.0.1", listen_port: int = 1080):
        self.node_link = node_link
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.proc = None
        self.cfg_path = None

    def _find_binary(self):
        # prefer sing-box or singbox or singbox.exe on PATH
        for bin_name in ("sing-box", "singbox", "singbox.exe", "sing-box.exe"):
            path = shutil.which(bin_name)
            if path:
                return path
        return None

    def _build_config(self):
        # Best-effort parsing: if node_link looks like a full proxy URL (socks/http), we do nothing
        if not self.node_link or self.node_link.startswith(("http://", "https://", "socks5://", "socks5h://")):
            return None

        # For common URL schemes (vmess/vless/hysteria2), we create a very small outlet -> inbound mapping
        # This is a simplification; for production use you should rely on a battle-tested generator (optiklink-sg)
        cfg = {
            "log": {"level": "info"},
            "inbounds": [
                {
                    "type": "socks",
                    "listen": self.listen_addr,
                    "listenPort": self.listen_port
n                }
            ],
            "outbounds": [
                {
                    "type": "direct"
                }
            ]
        }
        return cfg

    def start(self) -> bool:
        # If node_link already an explicit proxy URL, we don't need to run sing-box here
        if self.node_link and self.node_link.startswith(("http://", "https://", "socks5://", "socks5h://")):
            # nothing to start
            return True

        bin_path = self._find_binary()
        if not bin_path:
            print("❌ sing-box binary not found on PATH. Please install sing-box or provide a local proxy via SINGBOX_PROXY.")
            return False

        cfg = self._build_config()
        if cfg is None:
            print("⚠️ Could not build sing-box config from NODE_LINK; treat NODE_LINK as local proxy or use optiklink-sg generator.")
            return False

        fd, self.cfg_path = tempfile.mkstemp(prefix="singbox_cfg_", suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump(cfg, f)

        try:
            # start sing-box with the config
            # try both `run` and legacy `client` subcommands if available; common usage is `sing-box run -c <file>`
            cmd = [bin_path, "run", "-c", self.cfg_path]
            self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception as e:
            print(f"❌ Failed to start sing-box: {e}")
            return False

        # wait for listen port to appear
        for _ in range(12):
            time.sleep(1)
            try:
                import socket
                with socket.socket() as s:
                    if s.connect_ex((self.listen_addr, self.listen_port)) == 0:
                        print(f"✅ sing-box socks5 is ready at {self.listen_addr}:{self.listen_port}")
                        return True
            except Exception:
                pass
        print("❌ sing-box did not open the expected port in time")
        return False

    def stop(self):
        if self.proc:
            try:
                os.killpg(os.getpgid(self.proc.pid), subprocess.signal.SIGTERM)
            except Exception:
                try:
                    self.proc.terminate()
                except Exception:
                    pass
            self.proc = None
        if self.cfg_path and os.path.exists(self.cfg_path):
            try:
                os.remove(self.cfg_path)
            except Exception:
                pass

    @property
    def proxy(self):
        return f"socks5h://{self.listen_addr}:{self.listen_port}"
