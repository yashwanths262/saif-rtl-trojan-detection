from pathlib import Path
import re


# ============================================================
# Find newest SAIF
# ============================================================

project_root = Path(__file__).resolve().parent.parent

saif_files = list(project_root.rglob("*.saif"))

if not saif_files:
    print("ERROR: No SAIF files found.")
    raise SystemExit

saif_file = max(saif_files, key=lambda f: f.stat().st_mtime)

print()
print("=" * 70)
print("SAIF TROJAN ANALYSIS")
print("=" * 70)

print("Using newest SAIF:")
print(saif_file)

print(f"\nFile size: {saif_file.stat().st_size} characters")


# ============================================================
# Read SAIF
# ============================================================

with open(
    saif_file,
    "r",
    encoding="utf-8",
    errors="ignore"
) as f:

    text = f.read()

print("\nSAIF file successfully opened.")


# ============================================================
# Extract INSTANCE blocks
# ============================================================

def extract_instances(text):

    instances = []

    pattern = re.compile(
        r"\(INSTANCE\s+([^\s\)]+)"
    )

    for match in pattern.finditer(text):

        name = match.group(1)

        start = match.start()

        depth = 0
        end = None

        for i in range(start, len(text)):

            if text[i] == "(":
                depth += 1

            elif text[i] == ")":

                depth -= 1

                if depth == 0:

                    end = i + 1
                    break

        if end is not None:

            instances.append(
                (name, text[start:end])
            )

    return instances


instances = extract_instances(text)


# ============================================================
# Parse TC values
# ============================================================

def parse_signals(instance_text):

    signals = {}

    # Split the instance into individual parenthesized
    # expressions and look for (TC number).

    pattern = re.compile(
        r"\(\s*([^\s\(\)]+)\s+"
        r"(?:\([^()]*\)\s*)*"
        r"\(TC\s+(\d+)\)"
    )

    for match in pattern.finditer(instance_text):

        signal = match.group(1)
        tc = int(match.group(2))

        signals[signal] = tc

    return signals


# ============================================================
# Analyze instances
# ============================================================

print()
print("=" * 70)
print("SAIF INSTANCES")
print("=" * 70)

instance_data = {}

for name, block in instances:

    signals = parse_signals(block)

    instance_data[name] = signals

    total_tc = sum(signals.values())

    print(
        f"Instance: {name:<20}"
        f"Signals: {len(signals):>4}"
        f" Total TC: {total_tc:>7}"
    )


# ============================================================
# Find Trojan instance
# ============================================================

# ============================================================
# Find Trojan DUT instance
# ============================================================

trojan_instance = None

for name, signals in instance_data.items():

    # Ignore testbench-level instance
    if name == "trojan_tb":
        continue

    signal_names = set(signals.keys())

    if "trojan_active" in signal_names:
        trojan_instance = name
        break

    if "trigger_condition" in signal_names:
        trojan_instance = name
        break

    if any(
        "internal_counter" in signal
        for signal in signal_names
    ):
        trojan_instance = name
        break


# ============================================================
# Find Golden instance
# ============================================================

golden_instance = None

for name, signals in instance_data.items():

    if name == "uut" and name != trojan_instance:

        golden_instance = name
        break


# ============================================================
# Classification
# ============================================================

if trojan_instance is not None:

    design_type = "TROJAN"

    dut_instance = trojan_instance

elif golden_instance is not None:

    design_type = "GOLDEN"

    dut_instance = golden_instance

else:

    design_type = "UNKNOWN"

    dut_instance = None


# ============================================================
# DUT data
# ============================================================

if dut_instance is not None:

    dut_signals = instance_data[dut_instance]

else:

    dut_signals = {}


dut_total_tc = sum(
    dut_signals.values()
)


# ============================================================
# Classification output
# ============================================================

print()
print("=" * 70)
print("DESIGN CLASSIFICATION")
print("=" * 70)

print(
    f"Design type       : {design_type}"
)

print(
    f"DUT instance      : "
    f"{dut_instance if dut_instance else 'Not found'}"
)


# ============================================================
# DUT switching
# ============================================================

print()
print("=" * 70)
print("DUT SWITCHING ACTIVITY")
print("=" * 70)

print(
    f"Total TC          : {dut_total_tc}"
)


# ============================================================
# Trojan analysis
# ============================================================

if design_type == "TROJAN":

    trojan_active = dut_signals.get(
        "trojan_active",
        None
    )

    trigger_condition = dut_signals.get(
        "trigger_condition",
        None
    )


    print()
    print("=" * 70)
    print("TROJAN STATUS")
    print("=" * 70)

    print(
        f"trojan_active     : "
        f"{trojan_active}"
    )

    print(
        f"trigger_condition : "
        f"{trigger_condition}"
    )


    # --------------------------------------------------------
    # Internal counter
    # --------------------------------------------------------

    counter_signals = {
        signal: tc
        for signal, tc
        in dut_signals.items()
        if "internal_counter" in signal
    }

    counter_total = sum(
        counter_signals.values()
    )


    print()
    print("=" * 70)
    print("TROJAN-SPECIFIC SWITCHING")
    print("=" * 70)

    if counter_signals:

        for signal, tc in counter_signals.items():

            print(
                f"{signal:<30} TC = {tc}"
            )

        print("-" * 70)

        print(
            f"Internal counter TC : "
            f"{counter_total}"
        )

    else:

        print(
            "No internal_counter signals found."
        )


    # --------------------------------------------------------
    # Trojan state
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TROJAN STATE")
    print("=" * 70)

    if (
        trojan_active == 0
        and trigger_condition == 0
    ):

        print(
            "STATUS: DORMANT"
        )

        print(
            "The Trojan payload did not activate."
        )

    elif trojan_active == 1:

        print(
            "STATUS: ACTIVE"
        )

    else:

        print(
            "STATUS: CHECK REQUIRED"
        )


# ============================================================
# Final summary
# ============================================================

print()
print("=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(
    f"SAIF file         : {saif_file.name}"
)

print(
    f"Design type       : {design_type}"
)

print(
    f"DUT total TC      : {dut_total_tc}"
)

if design_type == "TROJAN":

    print(
        f"Trojan active     : "
        f"{trojan_active}"
    )

    print(
        f"Trigger condition : "
        f"{trigger_condition}"
    )

    print(
        f"Trojan counter TC : "
        f"{counter_total}"
    )

print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)