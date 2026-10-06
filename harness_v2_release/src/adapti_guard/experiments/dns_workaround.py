"""Resolve API hostnames when system DNS (/etc/resolv.conf) is missing.

Uses UDP queries to a public resolver (8.8.8.8). Does not log secrets.
"""

from __future__ import annotations

import socket
import struct
from functools import lru_cache

_PATCHED = False
_ORIG = socket.getaddrinfo


def _udp_a_records(name: str, dns: str = "8.8.8.8") -> list[str]:
    tid = b"\x12\x34"
    header = tid + b"\x01\x00" + b"\x00\x01\x00\x00\x00\x00\x00\x00"
    qname = b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\x00"
    msg = header + qname + b"\x00\x01\x00\x01"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        sock.sendto(msg, (dns, 53))
        data, _ = sock.recvfrom(512)
    finally:
        sock.close()
    i = 12
    while i < len(data) and data[i]:
        i += 1 + data[i]
    i += 5
    ancount = struct.unpack("!H", data[6:8])[0]
    ips: list[str] = []
    for _ in range(ancount):
        if i >= len(data):
            break
        if data[i] & 0xC0:
            i += 2
        else:
            while i < len(data) and data[i]:
                i += 1 + data[i]
            i += 1
        if i + 10 > len(data):
            break
        rtype, _rclass, _ttl, rdlen = struct.unpack("!HHIH", data[i : i + 10])
        i += 10
        rdata = data[i : i + rdlen]
        i += rdlen
        if rtype == 1 and rdlen == 4:
            ips.append(socket.inet_ntoa(rdata))
    return ips


@lru_cache(maxsize=64)
def resolve_hostname(name: str) -> list[str]:
    return _udp_a_records(name)


def _patched_getaddrinfo(host, port, *args, **kwargs):
    if isinstance(host, str) and host not in ("8.8.8.8", "1.1.1.1", "127.0.0.1"):
        try:
            return _ORIG(host, port, *args, **kwargs)
        except OSError:
            ips = resolve_hostname(host)
            if not ips:
                raise
            results = []
            for ip in ips:
                results.extend(_ORIG(ip, port, *args, **kwargs))
            return results
    return _ORIG(host, port, *args, **kwargs)


def apply_public_dns_fallback() -> bool:
    """Patch socket.getaddrinfo if system DNS fails. Idempotent."""
    global _PATCHED
    if _PATCHED:
        return True
    try:
        socket.getaddrinfo("api.cerebras.ai", 443, type=socket.SOCK_STREAM)
        return False
    except OSError:
        socket.getaddrinfo = _patched_getaddrinfo  # type: ignore[assignment]
        _PATCHED = True
        return True
