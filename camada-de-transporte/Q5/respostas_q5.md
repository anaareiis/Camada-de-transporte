## Questão 5 — Vazão, Goodput e Overhead de Protocolo

**Stream analisado:** servidor `137.131.178.229:9000` → cliente (`tcp.stream eq 0`)
**Duração da captura:** 60,68 s

### Evidências
| Print | Descrição |
|-------|-----------|
| [`GRUPO11.png`](../GRUPO11.png) | Resumo da sessão no terminal do cliente (Total recebido / Throughput médio) |
| `Q5/Q5_conversations.png` | Statistics → Conversations (aba TCP), linha do stream com servidor:9000 |
| `Q5/Q5_iograph.png` | Statistics → IO Graph com a série `tcp.stream eq 0` em Bits/s |

---

### (a) Throughput médio reportado pelo cliente — é goodput ou throughput?

O cliente reportou no terminal:
- **Total recebido: 81,96 MB**
- **Throughput médio: 1,35 MB/s** (≈ 11,3 Mbps)

Esse valor é **GOODPUT**, não throughput bruto. O cliente mede `total += len(data)` a cada
`sock.recv()` e divide pelo tempo decorrido (`avg_tp = total / elapsed`). O `recv()` entrega à
aplicação **apenas o payload TCP, em ordem e sem duplicatas** — ou seja, não conta os cabeçalhos
Ethernet/IP/TCP nem os bytes retransmitidos. Portanto o cliente está medindo a taxa de **dados
úteis efetivamente entregues à aplicação** = goodput.

### (b) Vazão do mesmo stream no Wireshark — o que cada ferramenta mede?

**Statistics → Conversations (aba TCP)**, linha `137.131.178.229:9000 ↔ cliente`:
- Bytes B→A (servidor→cliente) ≈ **83,94 MB**
- Bytes totais da conversa ≈ **84,25 MB** (inclui os 0,31 MB de ACKs cliente→servidor)
- Bits/s B→A ≈ **11,6 Mbps**

**Statistics → IO Graph** com filtro `tcp.stream eq 0` em Bits/s:
- vazão média ao longo da sessão ≈ **11,5–11,6 Mbps** (com os platôs das pausas das Questões 2/3
  visíveis como quedas a zero).

Ambas medem **THROUGHPUT bruto** e **incluem os cabeçalhos** (contam o tamanho do frame
capturado — Ethernet + IP + TCP + payload) e também contam **retransmissões**. Diferença entre
elas: Conversations dá um total/média agregada; o IO Graph mostra a vazão instantânea ao longo
do tempo.

### (c) Comparação cliente × Wireshark

| Medida | Valor | Inclui cabeçalhos/retx? |
|--------|-------|--------------------------|
| Cliente (goodput) | 1,35 MB/s ≈ **11,3 Mbps** | Não |
| Wireshark IP | 1,376 MB/s ≈ **11,5 Mbps** | Sim (IP+TCP+payload) |
| Wireshark frame | 1,383 MB/s ≈ **11,6 Mbps** | Sim (Ethernet+IP+TCP+payload) |

Não são iguais. **O valor do Wireshark é maior** porque inclui o overhead dos cabeçalhos de
protocolo (e as retransmissões) que a aplicação nunca enxerga; o cliente conta só o payload útil.
A diferença observada (≈ 1,9 % no nível IP, ≈ 2,4 % no nível de frame) é da **mesma ordem de
grandeza** do overhead esperado dos cabeçalhos — coerente com o esperado.

### (d) Overhead percentual esperado vs. observado

Cálculo manual (cabeçalhos IP+TCP = 20 + 20 = 40 B sobre payload de 1390 B por segmento):

```
overhead (%) = cabeçalhos / (payload + cabeçalhos) × 100
             = 40 / (1390 + 40) × 100
             = 40 / 1430 × 100
             = 2,80 %
```

**Observado na captura:** overhead a nível IP = **1,87 %**, a nível de frame = **2,36 %**.

O resultado faz sentido: está na mesma faixa dos 2,80 % teóricos. A diferença observada ficou
**ligeiramente abaixo** do teórico por um motivo concreto — a placa de rede da máquina de captura
usou **segmentation offload (LRO/GRO)**: o payload médio por frame capturado foi de **2736 bytes**
(≈ 2 segmentos de 1390 B coalescidos num único frame), de modo que o trace registrou **um par de
cabeçalhos para cada ~2 segmentos** em vez de um par por segmento. Com menos cabeçalhos no trace
do que existiriam no fio físico, o overhead medido cai abaixo dos 2,80 % que valeriam para
segmentos individuais de 1390 B.

**Dados de apoio (extraídos do pcap):**
- Frames servidor→cliente: 31.419 (7 ACKs puros)
- Bytes na linha (frame): 88.016.313 B | Bytes IP: 87.576.423 B | Payload TCP: 85.942.675 B (81,96 MB ✓ bate com o cliente)
- Retransmissões: ~32 frames / ~85 KB (≈ 0,1 % do total → impacto desprezível na vazão)
