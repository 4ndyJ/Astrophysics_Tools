# Astrophysics_Tools
A space for me to put all my tools I create incase things get lost

Known Issues with Tools.py:
Tools.py requires [spaceKLIP](https://github.com/spacetelescope/spaceKLIP)'s starphot functions to work - this isnt a common thing to have so isnt imported in the __init__ files. This will change when I have the time to actually figure out what im doing with those functions
The following line needs to be in your bash file:
`export ATMO_2020_MODELS = /dir/where/you/saved/the/models/"`

Please consider if the models presented here are what are required! If in doubt, get into contact with the model's creators!
Current models included are:
  1) ATMO 2020 - a model set from Phillips et al. (2020) [http://perso.ens-lyon.fr/isabelle.baraffe/ATMO2020/]



## Download Instructions
Clone the repo (`git clone https://github.com/4ndyJ/Astrophysics_Tools`) into an environment you like (bear in mind the dependencies may differ from other packages you have)

cd into the directory (`cd /dir/where/you/saved/the/clone/`)

install via pip (`pip install -e .`), the directory above acts as the directory for the package (No need to move into site-pacakges)


