#!/usr/bin/env python3
"""
MCT-2600027 – Quick start demo
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import Orchestrator


def main():
    orch = Orchestrator()
    orch.demo_cycle()


if __name__ == "__main__":
    main()
