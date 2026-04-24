from __future__ import annotations

import random
from pathlib import Path


def generate_noise_block(seed: int, lines: int = 24) -> str:
    rng = random.Random(seed)
    ops = [
        lambda: (
            f"volatile int _cg_{rng.randint(1000,9999)} = "
            f"({rng.randint(1,255)} * 7 + 13) ^ 0x{rng.randint(0,65535):04X};"
        ),
        lambda: (
            f"for (volatile int _i{rng.randint(10,99)}=0; "
            f"_i{rng.randint(10,99)}<{rng.randint(1,5)}; _i{rng.randint(10,99)}++) {{}}"
        ),
        lambda: (
            f"volatile double _d{rng.randint(10,99)} = "
            f"(({rng.randint(1,90)}.0 / {rng.randint(2,99)}.0) * {rng.randint(1,500)}.0);"
        ),
        lambda: (
            f"if ({rng.randint(1,100)} > {rng.randint(200,300)}) "
            f"{{ return -{rng.randint(1,999)}; }}"
        ),
    ]
    return "\n".join(rng.choice(ops)() for _ in range(lines))


def generate_noise_header(seed: int, out_path: Path, lines: int = 24) -> Path:
    body = generate_noise_block(seed, lines=lines)
    content = (
        "#ifndef CERTIGUARD_DYNAMIC_NOISE_H\n"
        "#define CERTIGUARD_DYNAMIC_NOISE_H\n\n"
        "static inline int certiguard_dynamic_noise(void) {\n"
        f"{chr(10).join('  ' + line for line in body.splitlines())}\n"
        "  return 0;\n"
        "}\n\n"
        "#endif\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path

