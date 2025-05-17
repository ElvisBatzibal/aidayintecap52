python3 -m venv .venv
source .venv/bin/activate  # Para Mac/Linux
pip install -r requirements.txt
pip install --upgrade sentence-transformers transformers
python demo.py