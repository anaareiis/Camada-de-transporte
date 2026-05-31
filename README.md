# Trabalho Prático — Camada de Transporte

**Disciplina:** Teleinformática e Redes 2 — 2026/1  
**Grupo:** GRUPO11  
**Servidor:** `137.131.178.229:9000`

## Integrantes

| Nome | Matrícula |
|------|-----------|
| Ana Luísa Reis Nascente | 211045688 |
| Gabriel de Sousa | 211056000 |
| Marina Pimentel Moreno | 222014071 |

---

## Estrutura do Repositório

```
.
├── client.py              # Script de captura TCP fornecido
├── GRUPO11.pcap           # Captura de tráfego (60,6 s)
├── respostas.md           # Respostas completas Q1–Q5 com evidências
└── entrega_1/             # Relatório final (LaTeX / Overleaf)
    ├── main.tex
    ├── Logo_UnB.png
    ├── captura/           # Print do terminal durante a captura
    ├── resultados/        # Gráficos do sistema ABR (Q0 – Resultados)
    ├── Q1/                # Handshake TCP e parâmetros iniciais
    ├── Q2/                # Gráfico Stevens + zooms das interrupções
    ├── Q3/                # Window Scaling e algoritmo CUBIC
    ├── Q4/                # DupACKs, Out-of-Order e SACK
    └── Q5/                # Conversations e IO Graph (vazão/goodput)
```

---

## Questões Respondidas

| Issue | Questão | Tópico |
|-------|---------|--------|
| #2 | Captura | Sessão de captura com `client.py` — 60,6 s / 81,96 MB / 1,35 MB/s |
| #3 | Q1 | Three-way handshake: RTT = 34,96 ms · MSS = 1460 B · rwnd = 62.636 B |
| #4 | Q2 | Duas interrupções no gráfico Stevens (2,70 s e 4,45 s) |
| #5 | Q3 | Algoritmo CUBIC: Slow Start + retomada agressiva após interrupções |
| #6 | Q4 | 60 DupACKs · 26 Out-of-Order · 3 Fast Retransmissions · SACK ativo |
| #7 | Q5 | Goodput = 11,3 Mbps · overhead observado 2,36 % (esperado 2,80 %) |
| #8 | Relatório | Relatório LaTeX completo (`entrega_1/main.tex`) |

---

## Relatório LaTeX

O relatório está em `entrega_1/main.tex` e foi desenvolvido no **Overleaf**.

Para compilar localmente:

```bash
cd entrega_1
pdflatex main.tex
pdflatex main.tex   # segunda passagem para referências cruzadas
```

Requer: `texlive-full` ou equivalente com os pacotes `booktabs`, `float`, `enumitem`, `listings`, `hyperref`.
