# Respostas — Trabalho Prático: Camada de Transporte
**Grupo:** GRUPO11  
**Disciplina:** TR2 – 2026/1  
**Servidor:** 137.131.178.229:9000  
**Algoritmo TCP da máquina:** cubic  

---

## Sessão de Captura (Issue #2)

**Evidência:** `GRUPO11.png`, `GRUPO11.pcap`

- Duração: 60.6s
- Total recebido: 81.96 MB
- Throughput médio reportado pelo cliente: **1.35 MB/s**

---

## Questão 1 — Estabelecimento da Conexão e Parâmetros Iniciais (Issue #3)

**Evidência:** `Q1.png`

### Three-way handshake identificado na captura:

| Pacote | Timestamp | Flags | Origem |
|--------|-----------|-------|--------|
| SYN    | 19:52:15.002072 | `[S]`  | cliente → servidor |
| SYN-ACK | 19:52:15.037034 | `[S.]` | servidor → cliente |
| ACK    | 19:52:15.037074 | `[.]`  | cliente → servidor |

### Respostas:

**(a) RTT entre SYN e SYN-ACK:**  
**34.962 ms**  
Conforme campo `[The RTT to ACK the segment was: 34.962299 milliseconds]` visível em `[SEQ/ACK analysis]` do pacote SYN-ACK no Wireshark.

**(b) MSS negociado:**  
**1460 bytes**  
Ambos cliente e servidor anunciaram MSS = 1460 bytes nas Options do SYN e SYN-ACK respectivamente. O MSS efetivo é o mínimo dos dois, que neste caso é 1460 bytes.

**(c) Janela de recepção inicial (rwnd) anunciada pelo servidor no SYN-ACK:**  
**62.636 bytes**  
Campo Window Size Value do SYN-ACK. O servidor também negociou wscale = 7 (fator ×128), que passa a valer para os pacotes de dados subsequentes — mas o valor no próprio SYN-ACK é o raw, sem escalonamento.

---
