# Web 4.0, x402 Bazaar Protocol & Conway AI Automaton Specification

## 1. What is Web 4.0?

* **Web 1.0**: Read-Only Web (Static HTML, personal blogs).
* **Web 2.0**: Read-Write Social Web (User-generated content, centralized cloud platforms, ad-driven data harvesting).
* **Web 3.0**: Read-Write-Own Decentralized Web (Cryptocurrency wallets, DeFi, decentralized smart contracts).
* **Web 4.0**: **Autonomous Machine-to-Machine (M2M) Agentic Web**.
  * Software agents (LLMs, neural networks, sensor nodes, IoT devices) transact, negotiate, purchase compute, and settle micro-invoices autonomously without human intervention.

---

## 2. The x402 Bazaar Protocol (HTTP 402 "Payment Required")

HTTP status code **402 Payment Required** was reserved in the original 1990s HTTP standard for digital cash systems, but was never implemented because no native digital cash existed.

The **Qitcoin x402 Bazaar Protocol** activates native HTTP 402 using QTC micro-units (`qits`):

```
Client Agent                                   Server API Provider
    |                                                 |
    |---- GET /api/v1/quantum-compute --------------->|
    |                                                 |
    |<--- HTTP 402 Payment Required ------------------|
    |     Header: X-402-Pay-To: Q1Trillion...         |
    |     Header: X-402-Amount: 50,000 qits           |
    |     Header: X-402-Invoice: inv_98765            |
    |                                                 |
    |  [Client signs 0.05 QTC tx on Qitcoin L1]       |
    |                                                 |
    |---- POST /api/v1/quantum-compute -------------->|
    |     Header: X-402-Payment-Proof: <txid>         |
    |                                                 |
    |<--- HTTP 200 OK (Unlocked Computation Result) --|
```

### Why Qitcoin is Built for x402:
1. **6 Decimal Places (`qits`)**: Allows granular micropayments down to $0.000001$ QTC without rounding errors.
2. **Low-Fee UTXO Model**: Batched micropayment channels allow millions of M2M API calls with negligible overhead.

---

## 3. Conway AI Automaton & Self-Organizing Mesh

Qitcoin integrates Conway's Game of Life (B3/S23) cellular automaton to model emergent decentralized network dynamics:
* **Grid Topology**: 16x16 toroidal 2D lattice.
* **Nodes as Cells**: Active liquidity nodes represent living cells ($1$), dormant nodes represent dead cells ($0$).
* **Self-Healing Properties**:
  * If a cluster of nodes drops offline, the neighbor birth rule ($B3$) triggers automated reactivation of backup nodes.
  * Overcrowded pools experience death by overpopulation ($>3$ neighbors), preventing centralized liquidity concentration.
* **Live Visual Inspection**: Visible on the local web explorer at `http://localhost:8080`.
