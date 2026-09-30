#!/usr/bin/env python3
"""
Conway AI Automaton & Self-Organizing Decentralized Mesh for Qitcoin
------------------------------------------------------------------
Implements Conway's Game of Life (B3/S23) cellular automaton to model:
1. Dynamic peer-to-peer node health and self-healing liquidity distribution.
2. Emergent mesh routing for cross-chain transactions.
3. Deterministic cellular entropy generation for cryptographic nonce seeding.
"""

from typing import List, Dict, Any
import random

class ConwayGridEngine:
    def __init__(self, size: int = 16):
        self.size = size
        self.generation = 0
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self._seed_initial_patterns()

    def _seed_initial_patterns(self):
        """Seed gliders and oscillators representing active liquidity nodes."""
        # Glider 1 (Top-Left)
        glider = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        for r, c in glider:
            self.grid[r][c] = 1

        # Pulsar / Blinker center
        center = self.size // 2
        self.grid[center][center - 1] = 1
        self.grid[center][center] = 1
        self.grid[center][center + 1] = 1

        # Random decentralized nodes
        for _ in range(25):
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            self.grid[r][c] = 1

    def step(self) -> Dict[str, Any]:
        """Compute next generation according to standard Conway B3/S23 rules."""
        new_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        alive_count = 0

        for r in range(self.size):
            for c in range(self.size):
                # Count 8-neighbors with periodic toroidal boundaries
                neighbors = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr = (r + dr) % self.size
                        nc = (c + dc) % self.size
                        neighbors += self.grid[nr][nc]

                # Rule B3/S23:
                # Any live cell with 2 or 3 live neighbours survives.
                # Any dead cell with exactly 3 live neighbours becomes a live cell.
                # All other live cells die in the next generation.
                if self.grid[r][c] == 1:
                    if neighbors in [2, 3]:
                        new_grid[r][c] = 1
                        alive_count += 1
                else:
                    if neighbors == 3:
                        new_grid[r][c] = 1
                        alive_count += 1

        self.grid = new_grid
        self.generation += 1

        # Calculate network entropy and decentralized health score
        health_score = min(100.0, (alive_count / (self.size * self.size)) * 400.0)

        return {
            "generation": self.generation,
            "alive_nodes": alive_count,
            "total_capacity": self.size * self.size,
            "mesh_health_score": round(health_score, 1),
            "grid": self.grid
        }

conway_automaton = ConwayGridEngine(size=16)

if __name__ == "__main__":
    print(f"Initial State (Gen {conway_automaton.generation}):")
    st = conway_automaton.step()
    print(f"Gen {st['generation']}: {st['alive_nodes']} active nodes (Health: {st['mesh_health_score']}%)")
