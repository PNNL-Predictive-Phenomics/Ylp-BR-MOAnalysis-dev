# VaLPAS *Yarrowia lipolytical* analysis
This git repository contains the notebook and all required data files to reproduce the analysis of *y. lipolytica* metabolomics and proteomics associations via VaLPAS.

The Juptyer Notebook containing the analysis can be found [here](valpasAnalysis/analysis.ipynb).

## Dependencies

### python / conda

Currently depends mostly on [VaLPAS v1.0.0](https://github.com/PNNL-Predictive-Phenomics/valpas/releases/tag/v1.0.0).

This repository contains a included `conda` [environment file](valpasAnalysis/environment.yml) for easy dependency resolving.
For `conda` we recommend an install of [miniforge / condaforge](https://conda-forge.org/download/). For install instructions please refer to documentation there.

To create the conda environment from the supplied env file use the command below.

```sh
conda env create --file environment.yml
```

This should create an environment with the necessary dependencies that are needed to run the notebook.
Then boot up the `conda` environment (and potentially `jupyter` instance) as usual. Make sure to start the jupyter notebook from within this folder `valpasAnalysis` as the [analysis Notebook](valpasAnalysis/analysis.ipynb) contains relative filepaths based on this foledr as the rootfolder.

```sh
conda activate ylip-valpas-analysis
jupyter notebook # if the notebook is used via a webbrowser
```

## Usage

Once the dependencies are satisfied boot up a Jupyter instance and open the corresponding notebook.
