# elektrapy

elektrapy is a tool for the exploration of biotic electron flows in the environment.
The common pipeline consists in the functional annotation of metagenome-assembled genomes (MAGs) using [bigecyhmm](https://github.com/ArnaudBelcour/bigecyhmm) (Belcour et al., 2025).
With the predicted redox functions, elektrapy then builds an electron flow diagram (EFD) for visualizing how the electrons are transferred in the given samples, thus facilitating the identification of the major donors and acceptors.

An example presented at EBEC 2026 can be found in the [notebooks folder](notebooks/EFD-EBEC.ipynb).



# Installation

Future releases of elektrapy will include its installation as a Python package.
For its current usage, just the installation of the following Python packages is required: ```pandas, scikit-learn, plotly, networkx```
