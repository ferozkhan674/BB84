import random
import sys

# ─── ANSI colours ────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
MAGENTA= "\033[95m"
BLUE   = "\033[94m"
WHITE  = "\033[97m"

def colour(text, *codes):
    return "".join(codes) + str(text) + RESET

def banner(title: str, colour_code: str = CYAN):
    width = 62
    print()
    print(colour("╔" + "═" * (width-2) + "╗", colour_code, BOLD))
    print(colour("║" + title.center(width-2) + "║", colour_code, BOLD))
    print(colour("╚" + "═" * (width-2) + "╝", colour_code, BOLD))

def section(title: str):
    print(f"\n{colour('▸ ' + title, YELLOW, BOLD)}")
    print(colour("─" * 60, DIM))

def status(label: str, value, ok: bool | None = None):
    icon = ""
    if ok is True:  icon = colour("✓", GREEN, BOLD) + " "
    if ok is False: icon = colour("✗", RED,   BOLD) + " "
    print(f"  {colour(label + ':', DIM)}  {icon}{colour(value, WHITE)}")

# ─── Quantum primitives ───────────────────────────────────────────────────────

BASES = {"+": "rectilinear", "×": "diagonal"}

PHOTON_SYMBOLS = {
    # (basis, bit) → symbol
    ("+", 0): "→",
    ("+", 1): "↑",
    ("×", 0): "↗",
    ("×", 1): "↖",
}

def encode_photon(bit: int, basis: str) -> str:
    """Return the polarisation symbol for a given bit+basis."""
    return PHOTON_SYMBOLS[(basis, bit)]

def measure_photon(photon_symbol: str, sender_basis: str,
                   meas_basis: str) -> int:
    """
    Quantum measurement:
    - Same basis → perfectly recovers the bit.
    - Different basis → 50 % random outcome (quantum indeterminacy).

    sender_basis is the basis in which the photon was *encoded*
    (Alice's basis, or Eve's re-encoding basis).
    """
    # Recover the bit from the photon's encoding basis (not Alice's original)
    photon_basis = None
    original_bit = None
    for (b, bit_val), sym in PHOTON_SYMBOLS.items():
        if sym == photon_symbol:
            photon_basis = b
            original_bit = bit_val
            break

    # If Bob's basis matches the photon's actual encoding basis → correct read
    if photon_basis is not None and meas_basis == photon_basis:
        return original_bit
    else:
        return random.randint(0, 1)   # quantum randomness

# ─── Protocol steps ───────────────────────────────────────────────────────────

def alice_prepare(n: int):
    """Step 1 – Alice generates bits and bases, encodes photons."""
    bits  = [random.randint(0, 1) for _ in range(n)]
    bases = [random.choice(["+", "×"]) for _ in range(n)]
    photons = [encode_photon(b, bs) for b, bs in zip(bits, bases)]
    return bits, bases, photons

def eve_intercept(photons: list[str], alice_bases: list[str]) -> tuple:
    """
    Eve measures every photon with a random basis, then re-sends
    a new photon based on her measurement result.  This introduces
    ~25 % errors into the Alice-Bob key.
    """
    eve_bases   = [random.choice(["+", "×"]) for _ in photons]
    eve_bits    = []
    new_photons = []
    for photon, a_basis, e_basis in zip(photons, alice_bases, eve_bases):
        measured = measure_photon(photon, a_basis, e_basis)
        eve_bits.append(measured)
        new_photons.append(encode_photon(measured, e_basis))
    return eve_bits, eve_bases, new_photons

def bob_measure(photons: list[str], alice_bases: list[str]) -> tuple:
    """Bob picks random bases and measures each photon."""
    bob_bases = [random.choice(["+", "×"]) for _ in photons]
    bob_bits  = [measure_photon(p, ab, bb)
                 for p, ab, bb in zip(photons, alice_bases, bob_bases)]
    return bob_bits, bob_bases

def sift(alice_bits, alice_bases, bob_bits, bob_bases):
    """Keep only the positions where Alice and Bob chose the same basis."""
    key_alice, key_bob, positions = [], [], []
    for i, (ab, bb) in enumerate(zip(alice_bases, bob_bases)):
        if ab == bb:
            key_alice.append(alice_bits[i])
            key_bob.append(bob_bits[i])
            positions.append(i)
    return key_alice, key_bob, positions

def error_rate(key_alice: list[int], key_bob: list[int],
               sample_frac: float = 0.25) -> float:
    """
    Publicly compare a random sample of sifted bits to estimate QBER
    (Quantum Bit Error Rate).  Real systems sacrifice these bits.
    """
    n_sample = max(1, int(len(key_alice) * sample_frac))
    indices  = random.sample(range(len(key_alice)), n_sample)
    errors   = sum(1 for i in indices if key_alice[i] != key_bob[i])
    return errors / n_sample

def bits_to_hex(bits: list[int]) -> str:
    """Pack bits into a hex string (padded to full bytes)."""
    if not bits:
        return "(empty)"
    pad = (-len(bits)) % 8
    bits_padded = bits + [0] * pad
    value = int("".join(str(b) for b in bits_padded), 2)
    n_hex = (len(bits_padded)) // 4
    return format(value, f"0{n_hex}X")

# ─── Pretty-print helpers ─────────────────────────────────────────────────────

def print_qubit_table(n_show: int, alice_bits, alice_bases, photons,
                      eve_bits, eve_bases, eve_photons,
                      bob_bits, bob_bases, sift_positions, has_eve: bool):
    """Print a compact table of the first n_show qubits."""
    cols = min(n_show, len(alice_bits))
    idx_row   = "  #   " + "".join(f"{i:^5}" for i in range(cols))
    print(colour(idx_row, DIM))

    def row(label, values, colour_fn=None):
        cells = ""
        for v in values[:cols]:
            cell = f"{str(v):^5}"
            cells += colour_fn(cell) if colour_fn else cell
        print(f"  {colour(label, CYAN):<20}{cells}")

    row("Alice bits",    alice_bits)
    row("Alice bases",   alice_bases,
        lambda c: colour(c, MAGENTA) if "×" in c else colour(c, BLUE))
    row("Photons sent",  photons)

    if has_eve:
        row("Eve bases",     eve_bases,
            lambda c: colour(c, RED))
        row("Eve bits",      eve_bits,
            lambda c: colour(c, RED))
        row("Eve re-sends",  eve_photons,
            lambda c: colour(c, RED))

    row("Bob bases",     bob_bases,
        lambda c: colour(c, MAGENTA) if "×" in c else colour(c, BLUE))
    row("Bob bits",      bob_bits)

    sift_set = set(sift_positions)
    match_row = "  " + colour("Basis match?", CYAN) + "          "
    for i in range(cols):
        cell = " ✓  " if i in sift_set else " ✗  "
        match_row += colour(cell, GREEN) if i in sift_set else colour(cell, DIM)
    print(match_row)

# ─── Main simulation ──────────────────────────────────────────────────────────

def run_simulation(n_qubits: int = 64,
                   eve_present: bool = False,
                   qber_threshold: float = 0.11,
                   show_qubits: int = 16,
                   verbose: bool = True):

    banner("BB84 Quantum Key Distribution Simulation")

    print(f"""
  {colour('Protocol:', CYAN)} BB84 (Bennett & Brassard, 1984)
  {colour('Qubits:',   CYAN)} {n_qubits}
  {colour('Eve:',      CYAN)} {'YES — eavesdropper active!' if eve_present else 'No'}
  {colour('QBER threshold:', CYAN)} {qber_threshold*100:.1f}%  (abort if exceeded)
""")

    # ── Step 1 ────────────────────────────────────────────────────────────────
    section("Step 1 · Alice prepares & sends qubits")
    alice_bits, alice_bases, photons = alice_prepare(n_qubits)
    print(f"  Alice generated {n_qubits} random bits and polarised photons.")
    print(f"  Bases used:  {colour('+', BLUE)} rectilinear  "
          f"{colour('×', MAGENTA)} diagonal")

    # ── Step 2 (optional Eve) ─────────────────────────────────────────────────
    eve_bits = eve_bases = eve_photons = None
    channel_photons = photons          # what Bob actually receives

    if eve_present:
        section("Step 2 · Eve intercepts the quantum channel")
        eve_bits, eve_bases, eve_photons = eve_intercept(photons, alice_bases)
        channel_photons = eve_photons
        print(colour("  ⚠  Eve measures every qubit with a random basis and", RED))
        print(colour("     re-sends a new photon.  ~25 % errors expected.", RED))

    # ── Step 3 ────────────────────────────────────────────────────────────────
    section("Step 3 · Bob measures incoming qubits")
    bob_bits, bob_bases = bob_measure(channel_photons, alice_bases)
    print(f"  Bob chose random bases and recorded his measurements.")

    # ── Qubit table ───────────────────────────────────────────────────────────
    section(f"Qubit-level view  (first {show_qubits} of {n_qubits})")
    key_a_tmp, key_b_tmp, sift_pos_tmp = sift(
        alice_bits, alice_bases, bob_bits, bob_bases)
    print_qubit_table(
        show_qubits,
        alice_bits, alice_bases, photons,
        eve_bits or [], eve_bases or [], eve_photons or [],
        bob_bits, bob_bases, sift_pos_tmp, eve_present
    )

    # ── Step 4 – Sifting ──────────────────────────────────────────────────────
    section("Step 4 · Basis reconciliation (sifting)")
    key_alice, key_bob, sift_positions = sift(
        alice_bits, alice_bases, bob_bits, bob_bases)

    match_count = len(sift_positions)
    efficiency  = match_count / n_qubits * 100
    status("Qubits sent",          n_qubits)
    status("Matching bases",       f"{match_count}  ({efficiency:.1f}%)")
    status("Sifted key length",    f"{match_count} bits")

    # ── Step 5 – Error estimation ─────────────────────────────────────────────
    section("Step 5 · Error-rate check (QBER estimation)")
    qber = error_rate(key_alice, key_bob)
    qber_pct = qber * 100

    qber_colour = GREEN if qber < qber_threshold else RED
    status("Measured QBER", f"{qber_pct:.1f}%",
           ok=(qber < qber_threshold))
    status("Threshold",     f"{qber_threshold*100:.1f}%")

    # ── Step 6 – Decision ─────────────────────────────────────────────────────
    section("Step 6 · Security decision")
    secure = qber < qber_threshold

    if secure:
        # Remove the sample bits (sacrificed for QBER check)
        n_sample = max(1, int(len(key_alice) * 0.25))
        sample_idx = set(random.sample(range(len(key_alice)), n_sample))
        final_key_alice = [b for i, b in enumerate(key_alice) if i not in sample_idx]
        final_key_bob   = [b for i, b in enumerate(key_bob)   if i not in sample_idx]

        remaining_errors = sum(a != b for a, b in zip(final_key_alice, final_key_bob))

        print(colour("  ✓  Channel appears secure.  Key accepted.", GREEN, BOLD))
        status("Final key length",   f"{len(final_key_alice)} bits")
        status("Remaining errors",   remaining_errors,
               ok=(remaining_errors == 0))
        status("Alice's key (hex)",  bits_to_hex(final_key_alice))
        status("Bob's key   (hex)",  bits_to_hex(final_key_bob))
        keys_match = final_key_alice == final_key_bob
        status("Keys identical?",    "Yes ✓" if keys_match else "No ✗",
               ok=keys_match)
    else:
        print(colour("  ✗  QBER too high — eavesdropping suspected!", RED, BOLD))
        print(colour("     Alice and Bob abort.  No key is used.", RED))

    # ── Summary ───────────────────────────────────────────────────────────────
    banner("Simulation Summary", GREEN if secure else RED)
    print(f"""
  {'Eve active:':26} {colour('YES', RED, BOLD) if eve_present else colour('No', GREEN)}
  {'Sifted bits:':26} {match_count} / {n_qubits}  ({efficiency:.1f}% efficiency)
  {'QBER:':26} {colour(f'{qber_pct:.1f}%', qber_colour, BOLD)}
  {'Outcome:':26} {colour('KEY ACCEPTED  ✓', GREEN, BOLD) if secure
                   else colour('KEY REJECTED  ✗', RED,   BOLD)}
""")
    return secure

# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    print(colour("""
  ╔══════════════════════════════════════════════╗
  ║      BB84 QKD — Interactive Simulator        ║
  ╚══════════════════════════════════════════════╝
""", CYAN, BOLD))

    # Parse optional CLI args: python bb84_qkd.py [n_qubits] [--eve]
    n    = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 128
    eve  = "--eve" in sys.argv

    # Demo: run without Eve, then with Eve
    print(colour("  ══ Run 1: No eavesdropper ══", GREEN, BOLD))
    run_simulation(n_qubits=n, eve_present=False, show_qubits=14)

    print("\n" + colour("  ══ Run 2: Eve is present ══", RED, BOLD))
    run_simulation(n_qubits=n, eve_present=True,  show_qubits=14)

if __name__ == "__main__":
    main()
