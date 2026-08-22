# elektrapy

elektrapy is a tool for the exploration of biotic electron flows in the environment.
The common pipeline consists in the functional annotation of metagenome-assembled genomes (MAGs) using [bigecyhmm](https://github.com/ArnaudBelcour/bigecyhmm) (Belcour et al., 2025).
With the predicted redox functions, elektrapy then builds an electron flow diagram (EFD) for visualizing how the electrons are transferred in the given samples, thus facilitating the identification of the major donors and acceptors.

An example presented at EBEC 2026 can be found in the [notebooks folder](notebooks/EFD-EBEC.ipynb).



# Installation

Future releases of elektrapy will include its installation as a Python package.
For its current usage, just the installation of the following Python packages is required: ```pandas, scikit-learn, plotly, networkx```



# Citation

The initial idea for visualizing electron flows in the environment was presented at Goldschmidt 2025, please cite as:

Climent Gargallo, G., Barosa, B., Cordone, A., & Giovannelli, D. (2025). Closing the circuit: Mapping the fate of electrons in the environment. https://conf.goldschmidt.info/goldschmidt/2025/meetingapp.cgi/Paper/27629


The version implemented in elektrapy differs substantially from that one and was presented at EBEC 2026, please cite as:

Climent Gargallo, G., de Pins, B., Moracci, M., & Edlmann, K. (2026). Disentangling the biotic flow of electrons in the continental subsurface. DOI: TBD
