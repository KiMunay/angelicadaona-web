import re
def _n(v):
    v=float(v); n=max(v-1,12) if v>12 else v
    return ('%g'%n)
def shrink(t):
    """Baja 1 px todos los tamaños de letra (mínimo 12 px; lo que ya es chico no se toca)."""
    t=re.sub(r'(font:\s*(?:italic\s+|oblique\s+)?\d{3}\s+)(\d+(?:\.\d+)?)px',lambda m:m.group(1)+_n(m.group(2))+'px',t)
    t=re.sub(r'(font-size:\s*)(\d+(?:\.\d+)?)px',lambda m:m.group(1)+_n(m.group(2))+'px',t)
    t=re.sub(r'(font-size:\s*clamp\()([^)]*)\)',lambda m:m.group(1)+re.sub(r'(\d+(?:\.\d+)?)px',lambda k:_n(k.group(1))+'px',m.group(2))+')',t)
    return t
