# elektrapy

elektrapy is a tool for the exploration of biotic electron flows in the environment.
The common pipeline consists in the functional annotation of metagenome-assembled genomes (MAGs) using [bigecyhmm](https://github.com/ArnaudBelcour/bigecyhmm) (Belcour et al., 2025).
With the predicted redox functions, elektrapy then builds an electron flow diagram (EFD) for visualizing how the electrons are transferred in the given samples, thus facilitating the identification of the major donors and acceptors.

An example Jupyter notebook can be found in the [notebooks folder](notebooks/Example-EFD.ipynb).



# Installation

Future releases of elektrapy will include its installation as a Python package.
For its current usage, just the installation of the following Python packages is required: ```pandas, scikit-learn, plotly, networkx```



# Citation

The initial idea for visualizing electron flows in the environment was presented at Goldschmidt 2025, please cite as:

Climent Gargallo, G., Barosa, B., Cordone, A., & Giovannelli, D. (2025). Closing the circuit: Mapping the fate of electrons in the environment. Goldschmidt2025 Abstracts. Goldschmidt2025. https://doi.org/10.7185/gold2025.27629


The version implemented in elektrapy differs substantially from that one and was presented at EBEC 2026, please cite as:

Climent Gargallo, G., De Pins, B., Moracci, M., & Edlmann, K. (2026). Disentangling the biotic flow of electrons in the continental subsurface. EBEC 2026.


The elektrapy package can be cited as:

Climent Gargallo, G. (2026). elektrapy: A tool for the exploration of biotic electron flows in the environment (Version 0.1.0) [Computer software]. https://github.com/guillecg/elektrapy



# References

Belcour, A., Megy, L., Stephant, S., Michel, C., Rad, S., Bombach, P., Dopffel, N., De Jong, H., & Ropers, D. (2025). Predicting coarse-grained representations of biogeochemical cycles from metabarcoding data. Bioinformatics, 41(Supplement_1), i49–i57. https://doi.org/10.1093/bioinformatics/btaf230
