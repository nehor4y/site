# cross_platform_netinfo.py
import socket
import os
import sys

def get_local_ip():
    # connect to public IP (no traffic sent) to get default outbound interface IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def get_gateway_on_unix():
    # Try reading /proc/net/route on Linux
    try:
        with open("/proc/net/route") as f:
            for line in f.readlines()[1:]:
                fields = line.strip().split()
                iface, dest, gateway = fields[0], fields[1], fields[2]
                if dest == "00000000":
                    gw = socket.inet_ntoa(bytes.fromhex(gateway))[::-1]
                    # Above reverse may be system-dependent; fallback to parsing with ip route
    except Exception:
        pass
    # fallback to 'ip route'
    try:
        import subprocess
        out = subprocess.check_output(["ip", "route"], text=True)
        for line in out.splitlines():
            if line.startswith("default"):
                parts = line.split()
                gw = parts[2]
                iface = parts[4] if "dev" in parts else None
                return gw, iface
    except Exception:
        return None, None

def main():
    ip = get_local_ip()
    print("Local IP:", ip)
    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        gw, iface = get_gateway_on_unix()
        print("Default Gateway:", gw)
        print("Interface (may be):", iface)
    else:
        # On Windows, use ipconfig
        import subprocess
        try:
            out = subprocess.check_output(["ipconfig"], text=True, encoding="utf-8", errors="ignore")
            print(out.splitlines()[:30])
        except Exception as e:
            print("Could not run ipconfig:", e)

if __name__ == "__main__":
    main()
