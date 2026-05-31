#!/usr/bin/env python3
"""
Analise da Questao 5 - Vazao, Goodput e Overhead.
Parser de pcap em Python puro (sem dependencias externas).
Calcula, para o stream TCP servidor->cliente:
  - bytes na "linha" (frame Ethernet completo)
  - bytes IP (IP total length)
  - bytes de payload TCP (goodput bruto)
  - throughput e goodput
  - overhead de cabecalhos
"""
import struct
import sys

PCAP = "/home/gabriel_pc/Testes/TR2/Camada-de-transporte/GRUPO11.pcap"
SERVER_IP = "137.131.178.229"
SERVER_PORT = 9000


def ip2str(b):
    return ".".join(str(x) for x in b)


def main():
    with open(PCAP, "rb") as f:
        data = f.read()

    magic = struct.unpack("<I", data[:4])[0]
    if magic in (0xa1b2c3d4, 0xa1b23c4d):
        endian = "<"
    elif magic in (0xd4c3b2a1, 0x4d3cb2a1):
        endian = ">"
    else:
        print("magic desconhecido:", hex(magic)); sys.exit(1)

    off = 24  # global header
    rec_hdr = endian + "IIII"

    n_pkts = 0
    # direcao servidor -> cliente
    s2c_frames = 0
    s2c_wire = 0          # soma do tamanho original do frame (incl. Ethernet 14B)
    s2c_ip_bytes = 0      # soma do IP total length
    s2c_tcp_payload = 0   # soma do payload TCP (dados uteis)
    s2c_pure_acks = 0
    # direcao cliente -> servidor
    c2s_frames = 0
    c2s_wire = 0
    c2s_tcp_payload = 0

    first_ts = None
    last_ts = None

    # para detectar retransmissoes grosseiramente (payload reenviado com seq <= max visto)
    max_seq_end = 0
    retx_frames = 0
    retx_bytes = 0

    L = len(data)
    while off + 16 <= L:
        ts_sec, ts_usec, incl_len, orig_len = struct.unpack(rec_hdr, data[off:off+16])
        off += 16
        pkt = data[off:off+incl_len]
        off += incl_len
        n_pkts += 1
        ts = ts_sec + ts_usec / (1e6 if magic in (0xa1b2c3d4, 0xd4c3b2a1) else 1e9)
        if first_ts is None:
            first_ts = ts
        last_ts = ts

        if len(pkt) < 14:
            continue
        eth_type = struct.unpack(">H", pkt[12:14])[0]
        if eth_type != 0x0800:  # IPv4
            continue
        ip = pkt[14:]
        if len(ip) < 20:
            continue
        ver_ihl = ip[0]
        ihl = (ver_ihl & 0x0f) * 4
        proto = ip[9]
        if proto != 6:  # TCP
            continue
        ip_total_len = struct.unpack(">H", ip[2:4])[0]
        src_ip = ip2str(ip[12:16])
        dst_ip = ip2str(ip[16:20])
        tcp = ip[ihl:]
        if len(tcp) < 20:
            continue
        src_port, dst_port = struct.unpack(">HH", tcp[0:4])
        seq = struct.unpack(">I", tcp[4:8])[0]
        data_off = (tcp[12] >> 4) * 4
        # payload TCP
        tcp_payload_len = ip_total_len - ihl - data_off
        if tcp_payload_len < 0:
            tcp_payload_len = 0

        is_s2c = (src_ip == SERVER_IP and src_port == SERVER_PORT)
        is_c2s = (dst_ip == SERVER_IP and dst_port == SERVER_PORT)

        if is_s2c:
            s2c_frames += 1
            s2c_wire += orig_len
            s2c_ip_bytes += ip_total_len
            s2c_tcp_payload += tcp_payload_len
            if tcp_payload_len == 0:
                s2c_pure_acks += 1
            # deteccao grosseira de retransmissao
            if tcp_payload_len > 0:
                seq_end = seq + tcp_payload_len
                if seq <= max_seq_end and seq_end <= max_seq_end:
                    retx_frames += 1
                    retx_bytes += tcp_payload_len
                if seq_end > max_seq_end:
                    max_seq_end = seq_end
        elif is_c2s:
            c2s_frames += 1
            c2s_wire += orig_len
            c2s_tcp_payload += tcp_payload_len

    dur = last_ts - first_ts
    MB = 1024 * 1024

    print("=" * 64)
    print("  ANALISE QUESTAO 5 - parser proprio (server -> cliente)")
    print("=" * 64)
    print(f"  Pacotes totais no arquivo : {n_pkts}")
    print(f"  Duracao da captura        : {dur:.3f} s")
    print("-" * 64)
    print(f"  [Servidor -> Cliente]")
    print(f"  Frames                    : {s2c_frames}")
    print(f"    dos quais ACKs puros    : {s2c_pure_acks} (payload=0)")
    print(f"  Bytes na linha (Eth+IP+TCP+payload) : {s2c_wire:,} B  = {s2c_wire/MB:.2f} MB")
    print(f"  Bytes IP (IP+TCP+payload)           : {s2c_ip_bytes:,} B  = {s2c_ip_bytes/MB:.2f} MB")
    print(f"  Payload TCP (dados uteis brutos)    : {s2c_tcp_payload:,} B  = {s2c_tcp_payload/MB:.2f} MB")
    print("-" * 64)
    print(f"  Retransmissoes (estim. grosseira)")
    print(f"    frames retransmitidos   : {retx_frames}")
    print(f"    bytes retransmitidos    : {retx_bytes:,} B")
    print(f"  Payload util (sem retx)   : {s2c_tcp_payload - retx_bytes:,} B = {(s2c_tcp_payload-retx_bytes)/MB:.2f} MB")
    print("-" * 64)
    # taxas
    def rate(b):
        return b / dur
    print("  THROUGHPUT (taxa bruta, na linha):")
    print(f"    {rate(s2c_wire)/MB:.3f} MB/s | {rate(s2c_wire)*8/1e6:.3f} Mbps (frame Ethernet)")
    print(f"    {rate(s2c_ip_bytes)/MB:.3f} MB/s | {rate(s2c_ip_bytes)*8/1e6:.3f} Mbps (camada IP)")
    print("  GOODPUT (payload util entregue a aplicacao):")
    gp = s2c_tcp_payload - retx_bytes
    print(f"    {rate(gp)/MB:.3f} MB/s | {rate(gp)*8/1e6:.3f} Mbps")
    print(f"    (payload bruto c/ retx: {rate(s2c_tcp_payload)/MB:.3f} MB/s)")
    print("-" * 64)
    # overhead
    if s2c_tcp_payload > 0:
        ov_wire = (s2c_wire - s2c_tcp_payload) / s2c_wire * 100
        ov_ip = (s2c_ip_bytes - s2c_tcp_payload) / s2c_ip_bytes * 100
        print(f"  Overhead observado (frame): {ov_wire:.2f}%")
        print(f"  Overhead observado (IP)   : {ov_ip:.2f}%")
    # overhead teorico para payload 1390 + 40 cabecalhos
    teo = 40 / (1390 + 40) * 100
    print(f"  Overhead teorico (40/(1390+40)): {teo:.2f}%")
    print("=" * 64)


if __name__ == "__main__":
    main()
