import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. Experimental data
# ============================================================

data = {
    "Seed": [
        1001, 1002, 1003, 1004, 1005,
        1006, 1007, 1008, 1009
    ],

    "Golden_TC": [
        969, 955, 982, 922, 974,
        949, 945, 967, 890
    ],

    "Trojan_TC": [
        1051, 1052, 1079, 1019, 1071,
        1046, 1014, 1042, 1064
    ]
}


df = pd.DataFrame(data)


# ============================================================
# 2. Calculate differences
# ============================================================

df["Difference"] = (
    df["Trojan_TC"] -
    df["Golden_TC"]
)


df["Percent_Increase"] = (
    df["Difference"] /
    df["Golden_TC"] *
    100
)


# ============================================================
# 3. Golden baseline statistics
# ============================================================

golden_mean = df["Golden_TC"].mean()

golden_std = df["Golden_TC"].std(
    ddof=1
)

golden_min = df["Golden_TC"].min()

golden_max = df["Golden_TC"].max()


# ============================================================
# 4. Trojan statistics
# ============================================================

trojan_mean = df["Trojan_TC"].mean()

trojan_std = df["Trojan_TC"].std(
    ddof=1
)


difference_mean = df["Difference"].mean()

difference_std = df["Difference"].std(
    ddof=1
)


percent_mean = df["Percent_Increase"].mean()


# ============================================================
# 5. Z-score relative to Golden baseline
# ============================================================

df["Trojan_Z"] = (
    df["Trojan_TC"] -
    golden_mean
) / golden_std


# ============================================================
# 6. Detection threshold
# ============================================================

# Initial statistical threshold:
# Golden mean + 3 standard deviations

threshold = (
    golden_mean +
    3 * golden_std
)


df["Detected"] = (
    df["Trojan_TC"] >
    threshold
)


# ============================================================
# 7. Print results
# ============================================================

print()
print("=" * 70)
print("HARDWARE TROJAN DETECTION ANALYSIS")
print("=" * 70)


print()
print("EXPERIMENTAL DATA")
print("-" * 70)

print(
    df.to_string(index=False)
)


print()
print("=" * 70)
print("GOLDEN BASELINE")
print("=" * 70)

print(
    f"Mean TC          : {golden_mean:.2f}"
)

print(
    f"Std deviation    : {golden_std:.2f}"
)

print(
    f"Minimum TC       : {golden_min}"
)

print(
    f"Maximum TC       : {golden_max}"
)


print()
print("=" * 70)
print("TROJAN RESULTS")
print("=" * 70)

print(
    f"Mean TC          : {trojan_mean:.2f}"
)

print(
    f"Std deviation    : {trojan_std:.2f}"
)

print(
    f"Mean difference  : {difference_mean:.2f} TC"
)

print(
    f"Difference std   : {difference_std:.2f} TC"
)

print(
    f"Mean increase    : {percent_mean:.2f}%"
)


print()
print("=" * 70)
print("ANOMALY THRESHOLD")
print("=" * 70)

print(
    f"Golden mean      : {golden_mean:.2f}"
)

print(
    f"Golden std       : {golden_std:.2f}"
)

print(
    f"Threshold (μ+3σ) : {threshold:.2f} TC"
)


print()
print("=" * 70)
print("Z-SCORE ANALYSIS")
print("=" * 70)

for _, row in df.iterrows():

    print(
        f"Seed {int(row['Seed'])}: "
        f"Trojan TC = {int(row['Trojan_TC'])}, "
        f"Z = {row['Trojan_Z']:.2f}, "
        f"Detected = {row['Detected']}"
    )


# ============================================================
# 8. Detection statistics
# ============================================================

detected_count = df["Detected"].sum()

total_trojan = len(df)

detection_rate = (
    detected_count /
    total_trojan *
    100
)


print()
print("=" * 70)
print("DETECTION RESULT")
print("=" * 70)

print(
    f"Trojan samples       : {total_trojan}"
)

print(
    f"Detected samples     : {detected_count}"
)

print(
    f"Detection rate       : {detection_rate:.2f}%"
)


# ============================================================
# 9. Save CSV
# ============================================================

df.to_csv(
    "trojan_detection_results.csv",
    index=False
)

print()
print(
    "Results saved to: "
    "trojan_detection_results.csv"
)


# ============================================================
# 10. Plot Golden vs Trojan
# ============================================================

plt.figure(
    figsize=(10, 6)
)

x = np.arange(
    len(df)
)

width = 0.35

plt.bar(
    x - width / 2,
    df["Golden_TC"],
    width,
    label="Golden"
)

plt.bar(
    x + width / 2,
    df["Trojan_TC"],
    width,
    label="Trojan"
)

plt.xticks(
    x,
    df["Seed"]
)

plt.xlabel(
    "Random Seed"
)

plt.ylabel(
    "Total Toggle Count (TC)"
)

plt.title(
    "Golden vs Dormant Trojan Switching Activity"
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "golden_vs_trojan.png",
    dpi=300
)

plt.show()


# ============================================================
# 11. Plot paired difference
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    x,
    df["Difference"]
)

plt.axhline(
    difference_mean,
    linestyle="--",
    label="Mean Difference"
)

plt.xticks(
    x,
    df["Seed"]
)

plt.xlabel(
    "Random Seed"
)

plt.ylabel(
    "Additional Toggle Count (TC)"
)

plt.title(
    "Additional Switching Activity Due to Trojan"
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "trojan_switching_difference.png",
    dpi=300
)

plt.show()


print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)