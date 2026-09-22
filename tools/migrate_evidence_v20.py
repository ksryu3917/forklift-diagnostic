#!/usr/bin/env python3
"""Copy registered legacy document bytes only after exact content-hash checks."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
assets = root / 'app/src/main/assets'
v20 = assets / 'v20'
entries = json.loads((v20 / 'evidence_registry.json').read_text())['entries']
for ref, record in entries.items():
    relative = Path(record['asset'])
    if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'evidence':
        raise ValueError(f'Unsafe evidence path: {ref}')
    destination = v20 / relative
    source = destination if destination.is_file() else assets / Path(*relative.parts[1:])
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError(f'Evidence content mismatch: {ref}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    print(f'EVIDENCE BYTE PARITY: {ref}; no field/runtime verification implied')
