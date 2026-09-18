# *Yarrowia lipolytica* Bioreactor growth, multi-omic Analyses

Scripts for data analysis and generating figures from bioreactor cultivation and multi-omic (proteomics, lipidomics, metabolomics) datasets of *Yarrowia lipolytica*.

- [Summary of Files](#summary-of-files)
- [Dependencies and Environment](#dependencies-and-environment)
- [Reference](#reference)
- [License](#license)

---

## Summary of Files
### VaLPAS workflow

Located and described in 'valpasAnalysis/' directory. 

### Notebooks
Located in `omicAnalysis/analysis/Notebooks/`:

- `00_proteometer_data_processing.ipynb` — Initial processing of proteomic and PTM raw data to obtain normalized values.
- `01_Proteomic_and_PCA_multi_omics.ipynb` — Multi-omic PCA visualization and proteomic log2FC and significance calculations.
- `01b_redox.ipynb` — Redox proteomics log2FC and significance calculations.
- `01c_phospho.ipynb` — Phosphoproteomics log2FC and significance calculations.
- `02_lipidAnalysis.ipynb` — Lipidomics data processing and analysis
- `03_lipid_Figs_pub_terpenoidPathway.ipynb` — Lipid pathway figures and terpenoid pathway proteomic figure for publication
- `04_enrichment_pipeline.ipynb` — Functional enrichment (GSEA, ORA) analysis pipeline for proteomic and PTM data.
- `05_gsea&miscFigures.ipynb` — Selected GSEA and miscellaneous figure generation.

### Raw Omic Data
Located in `omicAnalysis/analysis/Data/`:

- **DNA/** — Genome and CDS reference files (`W29.fasta`, gene catalog, GFF annotations)
- **Lipidomics/** — Raw and processed lipidomics expression data
- **Metabolomics/** — Metabolomics data (Pmart-normalized)
- **ProcessedData/** — Processed phospho, proteomics, and redox datasets with annotations
- **Proteomic_PTMs/** — Post-translational modification data (phospho, redox_global)

Functional and genome annotations used across analyses are in `omicAnalysis/analysis/Annotations/`.

### Bioreactor Data
Located in `reactorAnalysis/`:

- `Biostat2L_29` through `Biostat2L_35_highO2_noOmics` — Individual bioreactor run data, including BlueVis exports, experiment logs, and raw reactor output files (`.TXT`) organized by reactor/condition (e.g., control, oscillate, lowO2, highO2)
- `YarrowiaProcess_forPUB.ipynb` — Notebook for processing bioreactor process data for publication figures

---

## Dependencies and Environment

Analyses were performed in **Python (3.11)** within **Jupyter Notebooks**, using the conda environment `lipGSM`.



### Core scientific packages
```
numpy
pandas
scipy
scikit-learn
statsmodels
```

### Visualization packages
```
matplotlib
seaborn
matplotlib-venn
adjustText
```

### Omics / bioinformatics packages
```
gseapy
proteometer   # custom package used for normalization, PTM analysis,
              # quality control plots, rollup, and stats functions
              # rollup, and stats functions — see citation below

```

Analyses relied on the ProteoMeter package for multi-PTM and proteomics processing, normalization, and quality control:

Rozum JC, Sims AC, Li X, Sarkar S, Zhang T, Melchior JT, Ciesielski D, Pollock DD, Wiley HS, Qian W-J, Feng S. ProteoMeter: a pipeline for integrating multi-PTM and limited proteolysis data to reveal modification-structure coupling at the residue level. NAR Genomics and Bioinformatics. 2026;8(3):lqag073. https://doi.org/10.1093/nargab/lqag073


Source code: https://github.com/PNNL-Predictive-Phenomics/ProteoMeter

### Local / repo-specific modules
- `core.functions` — helper functions used across notebooks (included in this repo, not a pip package)

A full, pinned dependency list (including all sub-dependencies and exact versions) is available in [`lipGSM_environment.yml`](./lipGSM_environment.yml).

---
## Reference

This project is not yet published.

---

## License

Released under the Creative Commons 0 Public Domain Dedication: https://creativecommons.org/publicdomain/zero/1.0/

This material is free to use, and attribution is always appreciated. Attribution may be as follows:

> Authored by Czajka, Jeffrey J at the Pacific Northwest National Laboratory, operated by Battelle for the U.S. Department of Energy.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the United States Government nor the United States Department of Energy, nor the Contractor, nor any of their employees, nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness of any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe privately owned rights. Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United States Government or any agency thereof, or Battelle Memorial Institute. The views and opinions of authors expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

PACIFIC NORTHWEST NATIONAL LABORATORY operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY under Contract DE-AC05-76RL01830
