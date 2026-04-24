from __future__ import annotations

import random
from pathlib import Path


def generate_rule_noise_block(rng: random.Random, lines: int = 24) -> str:
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


def generate_smart_noise_block(rng: random.Random, lines: int = 24) -> str:
    """AI-inspired noise that looks like real validation logic."""
    templates = [
        "if (((({a} << 2) | ({b} >> 1)) & 0xFF) == 0x{c:02X}) {{ volatile int _tmp = {d}; }}",
        "volatile long _chk_{id} = (long)clock() ^ 0x{key:08X}; if (_chk_{id} < 0) return {ret};",
        "for (int _j=0; _j<{count}; _j++) {{ {var} = ({var} * {mul}) + {add}; }}",
        "volatile float _val_{id} = (float)sin({seed}.0) * {scale}f; if (_val_{id} > 1000.0f) exit(-1);",
        "if (({p1} ^ {p2}) == {p3}) {{ _dispatch_internal_call({id}); }}",
    ]
    
    block = []
    for _ in range(lines):
        t = rng.choice(templates)
        block.append(t.format(
            a=rng.randint(1, 255), b=rng.randint(1, 255), c=rng.randint(1, 255), d=rng.randint(1, 9999),
            id=rng.randint(1000, 9999), key=rng.getrandbits(32), ret=rng.randint(1, 100),
            count=rng.randint(2, 5), var=f"_v{rng.randint(1,99)}", mul=rng.randint(2, 10), add=rng.randint(1, 50),
            seed=rng.randint(1, 10000), scale=rng.randint(10, 100),
            p1=rng.randint(1, 100), p2=rng.randint(1, 100), p3=rng.randint(1, 100)
        ))
    return "\n".join(block)


def generate_polymorphic_noise_block(rng: random.Random, lines: int = 24) -> str:
    """Noise where variables and operations change roles randomly."""
    roles = ["state", "buffer", "key", "nonce", "counter"]
    vars_map = {role: f"_poly_{role}_{rng.randint(10,99)}" for role in roles}
    
    preamble = [f"volatile long {v} = {rng.getrandbits(16)};" for v in vars_map.values()]
    
    ops = [
        lambda: f"{vars_map['state']} = ({vars_map['state']} ^ {vars_map['key']}) + {rng.randint(1,100)};",
        lambda: f"{vars_map['buffer']} = ({vars_map['buffer']} << {rng.randint(1,3)}) | {vars_map['nonce']};",
        lambda: f"if ({vars_map['counter']}++ > {rng.randint(10,100)}) {{ {vars_map['key']} ^= {vars_map['state']}; }}",
        lambda: f"{vars_map['nonce']} = ({vars_map['nonce']} * {rng.randint(3,7)}) ^ {vars_map['buffer']};",
    ]
    
    body = [rng.choice(ops)() for _ in range(lines)]
    return "\n".join(preamble + body)


def generate_noise_header(seed: int, out_path: Path, mode: str = "rule", lang: str = "c", lines: int = 24) -> Path:
    rng = random.Random(seed)
    
    if mode == "rule":
        body = generate_rule_noise_block(rng, lines)
    elif mode == "smart":
        body = generate_smart_noise_block(rng, lines)
    elif mode == "polymorphic":
        body = generate_polymorphic_noise_block(rng, lines)
    else:
        raise ValueError(f"Unknown noise mode: {mode}")

    if lang == "c":
        content = (
            "#ifndef CERTIGUARD_DYNAMIC_NOISE_H\n"
            "#define CERTIGUARD_DYNAMIC_NOISE_H\n\n"
            "#include <math.h>\n"
            "#include <time.h>\n"
            "#include <stdlib.h>\n\n"
            "static inline void _dispatch_internal_call(int id) { (void)id; }\n\n"
            "static inline int certiguard_dynamic_noise(void) {\n"
            f"{chr(10).join('  ' + line for line in body.splitlines())}\n"
            "  return 0;\n"
            "}\n\n"
            "#endif\n"
        )
    elif lang == "csharp":
        # Convert C-style noise to C# style (simple replacements)
        cs_body = body.replace("volatile int", "int") # C# volatile is different, usually unnecessary for noise
        cs_body = cs_body.replace("volatile double", "double")
        cs_body = cs_body.replace("volatile float", "float")
        cs_body = cs_body.replace("volatile long", "long")
        cs_body = cs_body.replace("(float)sin", "(float)Math.Sin")
        cs_body = cs_body.replace("(long)clock()", "DateTime.Now.Ticks")
        cs_body = cs_body.replace("exit(-1);", "Environment.Exit(-1);")
        
        content = (
            "using System;\n\n"
            "namespace CertiGuard.Generated {\n"
            "    public static class DynamicNoise {\n"
            "        private static void _dispatch_internal_call(int id) { }\n\n"
            "        public static int Execute() {\n"
            f"{chr(10).join('            ' + line for line in cs_body.splitlines())}\n"
            "            return 0;\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
    else:
        raise ValueError(f"Unknown language: {lang}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path

