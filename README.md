 SAIF-Based RTL Switching Activity Analysis for Detection of Dormant Hardware Trojans

 Overview

Hardware Trojans are malicious modifications introduced into digital circuits. They may remain inactive until a specific trigger condition occurs, making them difficult to detect through conventional functional testing.

This project investigates whether switching activity at the Register Transfer Level (RTL) can be used to identify dormant Hardware Trojan circuitry before its payload is activated.

A Golden ALU implementation and a Trojan-inserted ALU implementation are simulated under identical randomized input workloads. Switching activity is extracted using the Switching Activity Interchange Format (SAIF) and analysed using Python.

 Objectives

- Analyse switching activity in Golden and Trojan-inserted RTL designs.
- Extract signal toggle counts from SAIF files.
- Identify additional switching activity associated with Trojan trigger-monitoring circuitry.
- Establish a statistical baseline using the Golden implementation.
- Detect anomalous switching activity using a three-standard-deviation threshold.
- Investigate whether dormant Trojan circuitry can be identified while the payload remains inactive.

 Tools and Technologies

- Verilog HDL
- Xilinx Vivado 2024.2
- XSim Simulator
- Switching Activity Interchange Format (SAIF)
- Python
- CSV-based result analysis

 Project Structure

```text
saif-rtl-trojan-detection/
│
├── rtl/
│   ├── golden_alu1.v
│   └── trojan_alu1.v
│
├── testbench/
│   ├── alu_tb.v
│   ├── golden_tb.v
│   └── trojan_tb.v
│
├── python/
│   ├── parse_saif1.py
│   ├── signal_analysis.py
│   ├── detection_analysis.py
│   └── final_detection.py
│
├── saif/
│   ├── golden/
│   └── trojan/
│
├── results/
│   ├── csv/
│   └── graphs/
│
├── vivado/
│   ├── HTD.xpr
│   └── HTD.srcs/
│
├── README.md
└── .gitignore
```

 Methodology

1. **RTL Design Preparation:** Develop a Golden ALU and a Trojan-inserted ALU containing additional trigger-monitoring circuitry.
2. **Simulation:** Apply identical randomized input workloads to both implementations using Vivado XSim.
3. **SAIF Generation:** Generate SAIF files to capture switching activity during simulation.
4. **SAIF Parsing:** Use Python scripts to extract toggle counts from the SAIF files.
5. **Signal Classification:** Separate common signals from Trojan-only signals.
6. **Statistical Analysis:** Calculate the Golden baseline mean, standard deviation and three-sigma threshold.
7. **Anomaly Detection:** Calculate Z-scores for the Trojan implementation and identify workloads exceeding the threshold.
8. **Signal-Level Analysis:** Examine the switching activity of Trojan-specific signals and compare common-signal activity.

 Experimental Results

The experiment was evaluated using nine matching Golden and Trojan workload pairs.

| Parameter | Result |
|---|---:|
| Golden average toggle count | 957.33 |
| Golden standard deviation | 17.87 |
| Trojan average toggle count | 1048.67 |
| Average additional toggle count | 91.33 |
| Average switching increase | 9.54% |
| Three-sigma threshold | 1010.94 |
| Trojan-only average activity | 97 |

The Trojan-specific signals included:

- `internal_counter[0]`
- `internal_counter[1]`
- `internal_counter[2]`
- `internal_counter[3]`
- `trigger_condition`
- `trojan_active`

The trigger condition and Trojan payload remained inactive during the evaluated workloads. However, the trigger-monitoring circuitry produced measurable switching activity.

All 9 of the evaluated Trojan workloads exceeded the experimental three-sigma detection threshold.

 Results and Visualisation

The `results/graphs/` directory contains:

1. Total switching activity comparison between Golden and Trojan designs.
2. Z-score-based anomaly detection.
3. Trojan-only signal switching activity.
4. Common-signal switching activity difference.

The `results/csv/` directory contains the corresponding numerical analysis results.

 Key Observation

The experiment demonstrates that dormant Hardware Trojan circuitry can generate measurable switching activity even when its trigger condition and payload remain inactive.

Signal-level analysis helps distinguish activity associated with Trojan-specific circuitry from normal switching activity in common circuit signals.

 Limitations

- The current evaluation uses one Trojan architecture.
- The experiment uses nine randomized workloads.
- The statistical threshold is established from the evaluated Golden baseline.
- The results are based on RTL simulation and do not represent direct physical power measurements.
- Further independent validation is required before making claims about general detection accuracy.

 Future Work

- Evaluate multiple Hardware Trojan architectures and trigger mechanisms.
- Increase the number and diversity of input workloads.
- Validate the detection method using independent test workloads.
- Extend the analysis to gate-level netlists and simulations.
- Investigate physical power estimation using switching activity and capacitance information.
- Explore machine-learning-based anomaly detection.
- Develop automatic identification and localisation of suspicious RTL signals.

 Conclusion

This project presents an RTL switching-activity-based approach for identifying dormant Hardware Trojan circuitry using SAIF data and statistical analysis.

The experimental results indicate that additional switching activity from Trojan trigger-monitoring circuitry can provide an early indication of suspicious hardware modifications, even before the Trojan payload activates.

Further evaluation across different Trojan architectures, workloads and implementation levels is necessary to establish the broader applicability of the approach.
