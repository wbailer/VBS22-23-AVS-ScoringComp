# VBS22-23-AVS-ScoringComp
Comparison of VBS AVS scoring functions on VBS 2022 and VBS 2023 data.

For both competitions, the ranks of teams are compared when using the old (AVS) and new (AVS2) scoring functions. Spearman rank correlation coefficients for each task and overall results between both scoring functions are determined.

## Data

Please clone the [VBS 2022 AVS Analysis](https://github.com/sauterl/VBS22-AVS-Analysis.git) and [VBS 2023 Post-hoc Analysis](https://github.com/sauterl/VBS23-Post-Hoc-Analysis.git) repos to obtain the data. The paths are configured for having these two data repos as parallel directories to this one.

## Usage

Invoke the compary.py (adjust the data paths if needed)
Results (CSV files with the ranks per team in each competition and a file with all rank correlation coefficients) are written to ```./results```.
Precalculated results files are available.
