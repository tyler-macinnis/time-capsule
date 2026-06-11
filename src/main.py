"""Time Capsule — entry point."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft

from timecapsule.app import main

if __name__ == "__main__":
    ft.app(target=main)
