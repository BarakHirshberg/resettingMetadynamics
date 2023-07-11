import os
import numpy as np

# Example for a single trajectory with resetting in GROMACS

seed1 = 148157
seed2 = 163253
np.random.seed(seed1)

count = 0
time = 0
Passed = False
resettingRate = 1/500000

while not Passed:

    # Set system 
    
    nextTime = int(np.random.exponential(1/(2*resettingRate))) # Sample next resetting time
    os.mkdir("runDirectory")
    os.system("cp ala4.gro runDirectory")
    os.system("cp topol.top runDirectory")
    with open("ala4.mdp", "r") as file:
        lines = file.readlines()
    newfile = f"ld-seed = {seed1+count}\n gen-seed = {seed2+count}\n"
    for line in lines[2:]:
        newfile += line
    os.chdir("runDirectory")
    with open("ala4.mdp", "w") as file:
        file.write(newfile)
    
    # Run
    
    os.system("gmx_mpi grompp -f ala4.mdp -c ala4.gro -p topol.top -o ala4.tpr -maxwarn 4")
    os.system(f"gmx_mpi mdrun -s ala4.tpr  -nsteps {nextTime} -plumed ../plumed.dat")
    
    # Test for first-passage
    
    with open("PASS","r") as file:
        lines = file.readlines()
    if len(lines)!=0:
        time += float(lines[3].split()[0])
        Passed = True
    else:
        time += nextTime/500
        count += 1
    os.chdir("../")
    os.system("rm -r runDirectory")
        
# Example for a single trajectory with resetting in LAMMPS

seed = 148157

np.random.seed(seed)

count = 0
time = 0
Passed = False
resettingRate = 1/500000
mass = 40
std = np.sqrt((8.31445e-7 * 300 / mass))

while not Passed:

    # Set system 
    
    nextTime = int(np.random.exponential(1/resettingRate)) # Sample next resetting time
    V1 = np.random.normal(0, std)
    V2 = np.random.normal(0, std)

    with open("twoWellsModel.lmp", "r") as file:
        lines = file.readlines()
    newfile = ""
    for line in lines[:10]:
        newfile += line
    newfile += f"velocity    all set {V1} {V2} 0 sum yes\n"
    for line in lines[11:17]:
        newfile += line
    newfile += f"fix        2  all langevin 300 300 100.0 {seed + count}\n"  
    for line in lines[18:-1]:
        newfile += line
    newfile += f"run {nextTime}"    
    with open("newRun.lmp", "w") as file:
        file.write(newfile)
    
    # Run
    
    os.system(f"mpirun LAMMPSfullAddress -in newRun.lmp -log none -screen none")

    # Test for first-passage
    
    with open("PASS","r") as file:
        lines = file.readlines()
    if len(lines)!=0:
        time += float(lines[1].split()[0])
        Passed = True
    else:
        time += nextTime/1000
        count += 1
