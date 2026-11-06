import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# HARDWARE TROJAN DETECTION
# MULTI-FEATURE RTL SWITCHING ACTIVITY ANALYSIS
# ============================================================

BASE_DIR = Path(r"C:\Users\1by23\HTD")

INPUT_FILE = BASE_DIR / "switching_features.csv"
OUTPUT_FILE = BASE_DIR / "final_detection_results.csv"

print("=" * 70)
print("HARDWARE TROJAN DETECTION - FINAL ANALYSIS")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("\nLoaded data:")
print(df.to_string(index=False))

# ------------------------------------------------------------
# 2. GOLDEN BASELINE
# ------------------------------------------------------------

golden_total = df["Golden_Total_TC"]

golden_mean = golden_total.mean()
golden_std = golden_total.std(ddof=1)

threshold_3sigma = golden_mean + 3 * golden_std

print("\n" + "=" * 70)
print("GOLDEN BASELINE")
print("=" * 70)

print(f"Golden mean TC       : {golden_mean:.2f}")
print(f"Golden std deviation : {golden_std:.2f}")
print(f"3-sigma threshold    : {threshold_3sigma:.2f}")

# ------------------------------------------------------------
# 3. TOTAL SWITCHING Z-SCORE
# ------------------------------------------------------------

df["Total_Z_Score"] = (
    (df["Trojan_Total_TC"] - golden_mean)
    / golden_std
)

df["Total_Anomaly"] = df["Trojan_Total_TC"] > threshold_3sigma

# ------------------------------------------------------------
# 4. PERCENTAGE INCREASE
# ------------------------------------------------------------

df["Switching_Increase_Percent"] = (
    (df["Trojan_Total_TC"] - df["Golden_Total_TC"])
    / df["Golden_Total_TC"]
) * 100

# ------------------------------------------------------------
# 5. SIGNAL-LEVEL FEATURES
# ------------------------------------------------------------

# Additional switching produced by Trojan-specific circuitry
df["Trojan_Only_Activity"] = df["Trojan_Only_TC"]

# Change in switching of signals common to both designs
df["Common_Signal_Change"] = df["Common_Difference"]

# ------------------------------------------------------------
# 6. DORMANT TROJAN INDICATOR
# ------------------------------------------------------------

# A positive Trojan-only activity indicates additional circuitry
# switching even though the Trojan payload is dormant.

df["Dormant_Switching_Signature"] = (
    df["Trojan_Only_Activity"] > 0
)

# ------------------------------------------------------------
# 7. FINAL DETECTION
# ------------------------------------------------------------

# Statistical anomaly + additional switching signature

df["Trojan_Detected"] = (
    df["Total_Anomaly"]
    & df["Dormant_Switching_Signature"]
)

# ------------------------------------------------------------
# 8. SAVE RESULTS
# ------------------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

# ------------------------------------------------------------
# 9. PRINT FINAL TABLE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL DETECTION RESULTS")
print("=" * 70)

columns = [
    "Seed",
    "Golden_Total_TC",
    "Trojan_Total_TC",
    "Total_Difference",
    "Total_Z_Score",
    "Switching_Increase_Percent",
    "Common_Difference",
    "Trojan_Only_TC",
    "Trojan_Detected"
]

print(df[columns].to_string(index=False))

# ------------------------------------------------------------
# 10. DETECTION COUNT
# ------------------------------------------------------------

detected = df["Trojan_Detected"].sum()
total = len(df)

print("\n" + "=" * 70)
print("DETECTION SUMMARY")
print("=" * 70)

print(f"Detected samples : {detected}/{total}")
print(f"Detection rate   : {(detected / total) * 100:.2f}%")

# ------------------------------------------------------------
# 11. AVERAGE FEATURES
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("AVERAGE SWITCHING FEATURES")
print("=" * 70)

print(f"Golden total TC          : {df['Golden_Total_TC'].mean():.2f}")
print(f"Trojan total TC         : {df['Trojan_Total_TC'].mean():.2f}")
print(f"Total difference        : {df['Total_Difference'].mean():.2f}")
print(f"Common signal change    : {df['Common_Difference'].mean():.2f}")
print(f"Trojan-only activity    : {df['Trojan_Only_TC'].mean():.2f}")

# ------------------------------------------------------------
# 12. GRAPH 1 - TOTAL SWITCHING ACTIVITY
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    df["Seed"],
    df["Golden_Total_TC"],
    marker="o",
    label="Golden"
)

plt.plot(
    df["Seed"],
    df["Trojan_Total_TC"],
    marker="o",
    label="Trojan"
)

plt.axhline(
    threshold_3sigma,
    linestyle="--",
    label="Golden + 3σ Threshold"
)

plt.xlabel("Random Test Seed")
plt.ylabel("Total Switching Activity (TC)")
plt.title("Golden vs Trojan RTL Switching Activity")
plt.legend()
plt.grid(True)

plt.tight_layout()

plt.savefig(
    BASE_DIR / "01_total_switching_comparison.png",
    dpi=300
)

plt.show()

# ------------------------------------------------------------
# 13. GRAPH 2 - Z SCORE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    df["Seed"].astype(str),
    df["Total_Z_Score"]
)

plt.axhline(
    3,
    linestyle="--",
    label="3σ Detection Limit"
)

plt.xlabel("Random Test Seed")
plt.ylabel("Z-Score")
plt.title("Trojan Switching Activity Z-Score")
plt.legend()
plt.grid(True, axis="y")

plt.tight_layout()

plt.savefig(
    BASE_DIR / "02_zscore_detection.png",
    dpi=300
)

plt.show()

# ------------------------------------------------------------
# 14. GRAPH 3 - TROJAN ONLY ACTIVITY
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    df["Seed"].astype(str),
    df["Trojan_Only_TC"]
)

plt.xlabel("Random Test Seed")
plt.ylabel("Trojan-Only Switching Activity (TC)")
plt.title("Switching Activity of Trojan-Specific Logic")
plt.grid(True, axis="y")

plt.tight_layout()

plt.savefig(
    BASE_DIR / "03_trojan_only_activity.png",
    dpi=300
)

plt.show()

# ------------------------------------------------------------
# 15. GRAPH 4 - COMMON SIGNAL DIFFERENCE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    df["Seed"].astype(str),
    df["Common_Difference"]
)

plt.axhline(
    0,
    linestyle="-"
)

plt.xlabel("Random Test Seed")
plt.ylabel("Common Signal TC Difference")
plt.title("Change in Switching Activity of Common Signals")
plt.grid(True, axis="y")

plt.tight_layout()

plt.savefig(
    BASE_DIR / "04_common_signal_difference.png",
    dpi=300
)

plt.show()

# ------------------------------------------------------------
# 16. FINAL MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FILES CREATED")
print("=" * 70)

print(f"Results CSV : {OUTPUT_FILE}")
print("01_total_switching_comparison.png")
print("02_zscore_detection.png")
print("03_trojan_only_activity.png")
print("04_common_signal_difference.png")

print("\n" + "=" * 70)
print("FINAL ANALYSIS COMPLETE")
print("=" * 70)