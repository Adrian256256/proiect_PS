#!/bin/bash

# mergem în folderul proiectului
cd "$(dirname "$0")"

# activăm mediul virtual
source .venv/bin/activate

# pornim aplicația
python3 GSM_detector.py
