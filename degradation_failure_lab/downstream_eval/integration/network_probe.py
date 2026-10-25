"""Stdlib-only in-container observations; no Agent, model SDK or external DNS lookup."""
import errno
import json
from pathlib import Path
import socket
import struct
import sys

BLOCKED = {errno.ENETUNREACH, errno.EHOSTUNREACH, errno.EACCES, errno.EPERM,
           errno.EAFNOSUPPORT, errno.EPROTONOSUPPORT}


def attempt(family, kind, address, port, protocol=0, packet=b'network-isolation-probe', connect_only=False):
    stage = 'socket'
    try:
        with socket.socket(family, kind, protocol) as sock:
            sock.settimeout(0.4)
            stage = 'connect' if kind == socket.SOCK_STREAM else 'send'
            if kind == socket.SOCK_STREAM:
                sock.connect((address, port))
                if connect_only:
                    return {'outcome':'reachable', 'stage':'connect'}
                sock.sendall(packet)
            else:
                sock.sendto(packet, (address, port))
            stage = 'receive'
            data = sock.recv(512)
            return {'outcome':'reachable', 'received_bytes':len(data)}
    except TimeoutError:
        return {'outcome':'timeout', 'stage':stage}
    except OSError as error:
        return {'outcome':'blocked' if error.errno in BLOCKED else 'error',
                'stage':stage, 'errno':error.errno, 'error':str(error)}


def echo_packet(ipv6=False):
    packet = struct.pack('!BBHHH', 128 if ipv6 else 8, 0, 0, 1234, 1) + b'net-audit!'
    total = sum(struct.unpack('!%dH' % (len(packet)//2), packet))
    total = (total & 65535) + (total >> 16)
    total = (total & 65535) + (total >> 16)
    return packet[:2] + struct.pack('!H', ~total & 65535) + packet[4:]


def observe(targets):
    status = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    result = {'interfaces':[name for _, name in socket.if_nameindex()],
              'ipv4_routes':Path('/proc/net/route').read_text(),
              'ipv6_routes':Path('/proc/net/ipv6_route').read_text(),
              'resolver':Path('/etc/resolv.conf').read_text(),
              'capabilities':{key:status[key].strip() for key in ('CapEff','CapPrm','CapBnd','NoNewPrivs')},
              'probes':{}}
    # A local echo round trip proves the socket probe itself works, even without egress.
    with socket.socket() as server, socket.socket() as client:
        server.bind(('127.0.0.1', 0)); server.listen(1)
        client.settimeout(1); client.connect(server.getsockname())
        peer, _ = server.accept()
        with peer:
            client.sendall(b'local'); peer.sendall(peer.recv(5))
            result['loopback_control'] = client.recv(5) == b'local'
    for label, address in targets.items():
        family = socket.AF_INET6 if ':' in address else socket.AF_INET
        for channel, kind, port in [('tcp', socket.SOCK_STREAM, 8080),
                                    ('dns_tcp', socket.SOCK_STREAM, 53),
                                    ('dns_udp', socket.SOCK_DGRAM, 53),
                                    ('udp', socket.SOCK_DGRAM, 33434)]:
            result['probes'][label + '/' + channel] = attempt(family, kind, address, port)
        protocol = socket.IPPROTO_ICMPV6 if family == socket.AF_INET6 else socket.IPPROTO_ICMP
        result['probes'][label + '/icmp'] = attempt(
            family, socket.SOCK_DGRAM, address, 0, protocol, echo_packet(family == socket.AF_INET6))
        result['probes'][label + '/raw'] = attempt(
            family, socket.SOCK_RAW, address, 0, protocol, echo_packet(family == socket.AF_INET6))
    # Also check Docker's embedded resolver explicitly; ordinary route checks alone do not prove this.
    query = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + b'\x09isolation\x07invalid\x00\x00\x01\x00\x01'
    for address in ('127.0.0.1', '127.0.0.11'):
        result['probes']['resolver/' + address + '/udp'] = attempt(
            socket.AF_INET, socket.SOCK_DGRAM, address, 53, packet=query)
        result['probes']['resolver/' + address + '/tcp'] = attempt(
            socket.AF_INET, socket.SOCK_STREAM, address, 53, connect_only=True)
    # Linux packet sockets and VM host sockets must not provide an alternate egress path.
    for name, family, kind in [('packet', socket.AF_PACKET, socket.SOCK_RAW),
                               ('vsock', socket.AF_VSOCK, socket.SOCK_STREAM)]:
        try:
            with socket.socket(family, kind):
                value = {'outcome':'reachable', 'stage':'socket'}
        except OSError as error:
            value = {'outcome':'blocked' if error.errno in BLOCKED else 'error',
                     'stage':'socket', 'errno':error.errno, 'error':str(error)}
        result['probes']['socket/' + name] = value
    return result


if __name__ == '__main__':
    print(json.dumps(observe(json.loads(sys.argv[1]))))
