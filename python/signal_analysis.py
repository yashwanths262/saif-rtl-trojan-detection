from pathlib import Path
import re
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# FIND SAIF FILE
# ============================================================

def find_saif(filename):

    matches = list(PROJECT_ROOT.rglob(filename))

    if not matches:
        raise FileNotFoundError(
            f"Could not find {filename}"
        )

    return matches[0]


# ============================================================
# EXTRACT INSTANCE BLOCKS
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


# ============================================================
# PARSE SIGNALS
# ============================================================

def parse_signals(instance_text):

    signals = {}

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
# FIND ACTUAL DUT INSTANCE
# ============================================================

def read_dut_signals(saif_file):

    with open(
        saif_file,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        text = f.read()

    instances = extract_instances(text)

    candidates = []

    for name, block in instances:

        # ----------------------------------------------------
        # Ignore testbench-level instances
        # ----------------------------------------------------

        if name in {
            "golden_tb",
            "trojan_tb"
        }:
            continue

        if name.endswith("_tb"):
            continue


        signals = parse_signals(block)

        if not signals:
            continue


        signal_names = set(signals.keys())


        # ----------------------------------------------------
        # Score instance based on DUT-like signals
        # ----------------------------------------------------

        score = 0


        # Strong DUT indicators

        if "result[0]" in signal_names:
            score += 20

        if "alu_result[0]" in signal_names:
            score += 20


        # Normal ALU ports

        if "clk" in signal_names:
            score += 5

        if "reset" in signal_names:
            score += 5

        if "enable" in signal_names:
            score += 5

        if "A[0]" in signal_names:
            score += 5

        if "B[0]" in signal_names:
            score += 5

        if "op[0]" in signal_names:
            score += 5


        # Trojan indicators

        if "trojan_active" in signal_names:
            score += 50

        if "trigger_condition" in signal_names:
            score += 50

        if any(
            "internal_counter" in signal
            for signal in signal_names
        ):
            score += 50


        candidates.append(
            (
                score,
                name,
                signals
            )
        )


    # --------------------------------------------------------
    # No candidate
    # --------------------------------------------------------

    if not candidates:

        raise RuntimeError(
            f"No DUT instance found in {saif_file}"
        )


    # --------------------------------------------------------
    # Select highest scoring DUT
    # --------------------------------------------------------

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    score, name, signals = candidates[0]


    print(
        f"  Selected DUT instance: "
        f"{name} "
        f"(score={score})"
    )


    return signals


# ============================================================
# START ANALYSIS
# ============================================================

print()
print("=" * 75)
print("RTL SWITCHING ACTIVITY - SIGNAL LEVEL ANALYSIS")
print("=" * 75)


golden_data = {}
trojan_data = {}


# ============================================================
# LOAD GOLDEN AND TROJAN SAIF FILES
# ============================================================

for seed in range(1001, 1010):


    # Golden mapping
    #
    # seed 1001 -> golden_baseline_02
    # seed 1002 -> golden_baseline_03
    # ...
    # seed 1009 -> golden_baseline_10

    golden_number = seed - 999

    golden_filename = (
        f"golden_baseline_{golden_number:02d}.saif"
    )


    # Trojan mapping
    #
    # seed 1001 -> trojan_dormant_01
    # seed 1002 -> trojan_dormant_02
    # ...
    # seed 1009 -> trojan_dormant_09

    trojan_number = seed - 1000

    trojan_filename = (
        f"trojan_dormant_{trojan_number:02d}.saif"
    )


    # Find files

    golden_file = find_saif(
        golden_filename
    )

    trojan_file = find_saif(
        trojan_filename
    )


    print()
    print(
        f"Seed {seed}:"
    )

    print(
        f"  Golden = "
        f"{golden_filename}"
    )

    print(
        f"  Trojan = "
        f"{trojan_filename}"
    )


    # Read DUT signals

    golden_data[seed] = read_dut_signals(
        golden_file
    )

    trojan_data[seed] = read_dut_signals(
        trojan_file
    )


# ============================================================
# SIGNAL SETS
# ============================================================

golden_signals = set()
trojan_signals = set()


for seed in range(1001, 1010):

    golden_signals.update(
        golden_data[seed].keys()
    )

    trojan_signals.update(
        trojan_data[seed].keys()
    )


# Signals present in both designs

common_signals = sorted(
    golden_signals &
    trojan_signals
)


# Signals existing only in Trojan

trojan_only_signals = sorted(
    trojan_signals -
    golden_signals
)


# Signals existing only in Golden

golden_only_signals = sorted(
    golden_signals -
    trojan_signals
)


# ============================================================
# PRINT SIGNAL CATEGORIES
# ============================================================

print()
print("=" * 75)
print("SIGNAL CATEGORIES")
print("=" * 75)

print(
    f"Common signals       : "
    f"{len(common_signals)}"
)

print(
    f"Trojan-only signals  : "
    f"{len(trojan_only_signals)}"
)

print(
    f"Golden-only signals  : "
    f"{len(golden_only_signals)}"
)


print()
print("Trojan-only signals:")

for signal in trojan_only_signals:

    print(
        f"  {signal}"
    )


# ============================================================
# SIGNAL-LEVEL DATASET
# ============================================================

rows = []


for seed in range(1001, 1010):

    golden = golden_data[seed]
    trojan = trojan_data[seed]


    # --------------------------------------------------------
    # Common signals
    # --------------------------------------------------------

    for signal in common_signals:

        golden_tc = golden.get(
            signal,
            0
        )

        trojan_tc = trojan.get(
            signal,
            0
        )

        difference = (
            trojan_tc -
            golden_tc
        )


        if golden_tc != 0:

            percent_change = (
                difference /
                golden_tc *
                100
            )

        else:

            percent_change = 0


        rows.append({

            "Seed": seed,

            "Signal": signal,

            "Category": "Common",

            "Golden_TC": golden_tc,

            "Trojan_TC": trojan_tc,

            "Difference": difference,

            "Percent_Change":
                percent_change

        })


    # --------------------------------------------------------
    # Trojan-only signals
    # --------------------------------------------------------

    for signal in trojan_only_signals:

        trojan_tc = trojan.get(
            signal,
            0
        )


        rows.append({

            "Seed": seed,

            "Signal": signal,

            "Category":
                "Trojan-only",

            "Golden_TC": 0,

            "Trojan_TC":
                trojan_tc,

            "Difference":
                trojan_tc,

            "Percent_Change": 0

        })


# Create DataFrame

signal_df = pd.DataFrame(
    rows
)


# ============================================================
# SAVE SIGNAL-LEVEL CSV
# ============================================================

signal_csv = (
    PROJECT_ROOT /
    "signal_level_results.csv"
)


signal_df.to_csv(
    signal_csv,
    index=False
)


# ============================================================
# FEATURE SUMMARY
# ============================================================

feature_rows = []


for seed in range(1001, 1010):

    golden = golden_data[seed]
    trojan = trojan_data[seed]


    # --------------------------------------------------------
    # Total activity
    # --------------------------------------------------------

    golden_total = sum(
        golden.values()
    )

    trojan_total = sum(
        trojan.values()
    )


    # --------------------------------------------------------
    # Common signal activity
    # --------------------------------------------------------

    golden_common = sum(
        golden.get(
            signal,
            0
        )
        for signal in common_signals
    )


    trojan_common = sum(
        trojan.get(
            signal,
            0
        )
        for signal in common_signals
    )


    # --------------------------------------------------------
    # Trojan-only activity
    # --------------------------------------------------------

    trojan_only_total = sum(
        trojan.get(
            signal,
            0
        )
        for signal in trojan_only_signals
    )


    # --------------------------------------------------------
    # Differences
    # --------------------------------------------------------

    total_difference = (
        trojan_total -
        golden_total
    )


    common_difference = (
        trojan_common -
        golden_common
    )


    # --------------------------------------------------------
    # Store features
    # --------------------------------------------------------

    feature_rows.append({

        "Seed":
            seed,

        "Golden_Total_TC":
            golden_total,

        "Trojan_Total_TC":
            trojan_total,

        "Total_Difference":
            total_difference,

        "Golden_Common_TC":
            golden_common,

        "Trojan_Common_TC":
            trojan_common,

        "Common_Difference":
            common_difference,

        "Trojan_Only_TC":
            trojan_only_total

    })


# Create feature DataFrame

feature_df = pd.DataFrame(
    feature_rows
)


# ============================================================
# SAVE FEATURE CSV
# ============================================================

feature_csv = (
    PROJECT_ROOT /
    "switching_features.csv"
)


feature_df.to_csv(
    feature_csv,
    index=False
)


# ============================================================
# PRINT FEATURE SUMMARY
# ============================================================

print()
print("=" * 75)
print("FEATURE SUMMARY")
print("=" * 75)

print(
    feature_df.to_string(
        index=False
    )
)


# ============================================================
# AVERAGE FEATURES
# ============================================================

print()
print("=" * 75)
print("AVERAGE FEATURES")
print("=" * 75)


print(
    f"Golden total TC       : "
    f"{feature_df['Golden_Total_TC'].mean():.2f}"
)


print(
    f"Trojan total TC       : "
    f"{feature_df['Trojan_Total_TC'].mean():.2f}"
)


print(
    f"Total difference      : "
    f"{feature_df['Total_Difference'].mean():.2f}"
)


print(
    f"Golden common TC      : "
    f"{feature_df['Golden_Common_TC'].mean():.2f}"
)


print(
    f"Trojan common TC      : "
    f"{feature_df['Trojan_Common_TC'].mean():.2f}"
)


print(
    f"Common difference     : "
    f"{feature_df['Common_Difference'].mean():.2f}"
)


print(
    f"Trojan-only TC        : "
    f"{feature_df['Trojan_Only_TC'].mean():.2f}"
)


# ============================================================
# TROJAN-ONLY SIGNAL AVERAGES
# ============================================================

print()
print("=" * 75)
print("TROJAN-ONLY SIGNAL AVERAGES")
print("=" * 75)


for signal in trojan_only_signals:

    values = []

    for seed in range(1001, 1010):

        values.append(
            trojan_data[seed].get(
                signal,
                0
            )
        )


    mean_tc = (
        sum(values) /
        len(values)
    )


    print(
        f"{signal:<35} "
        f"Mean TC = {mean_tc:.2f}"
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 75)
print("FILES CREATED")
print("=" * 75)


print(
    f"Signal-level data : "
    f"{signal_csv}"
)


print(
    f"Feature summary   : "
    f"{feature_csv}"
)


print()
print("=" * 75)
print("SIGNAL ANALYSIS COMPLETE")
print("=" * 75)