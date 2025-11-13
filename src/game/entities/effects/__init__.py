"""Entities effects package.

Expose small visual effect classes from this package for convenient imports.
"""
from .hitspark import Hitspark
FireInBody = None
Fireball = None
try:
	from .fireinbody import FireInBody as _FireInBody
	FireInBody = _FireInBody
except Exception:
	FireInBody = None

try:
	from .fireball import Fireball as _Fireball
	Fireball = _Fireball
except Exception:
	Fireball = None

# Export only the effects that loaded successfully
__all__ = ["Hitspark"]
if FireInBody is not None:
	__all__.append("FireInBody")
if Fireball is not None:
	__all__.append("Fireball")
