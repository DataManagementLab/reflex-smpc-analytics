# reflex-smpc-analytics
Reflex: Efficient and Flexible Intermediate Result Size Trimming for SMPC Query Execution


# This repo is for VLDB 2025 submission


# Instruction: How to use it

1. Download the MP-SPDZ to your local storage

you can use compiled version from: https://github.com/data61/MP-SPDZ/releases/download/v0.3.9/mp-spdz-0.3.9.tar.xz

or

you can compile it by yourself: https://github.com/data61/MP-SPDZ.git see README to follow the tutorial

2. move the .mpc files to /your-path/mp-spdz-your-version/Programs/Source/

you will see other example .mpc files in the directory

3. go back to the top entry /your-path/mp-spdz-your-version/

4. try to compile the .mpc code

./compile.py -R 128 -b 100000 [MPC file name]

if you successfully compiled the code, you should see a hash value to identify the runnable binary.

5. you can either run it locally or among three machines

Local: make sure you are in the top entry: /your-path/mp-spdz-your-version/

./Scripts/ring.sh [MPC file name]


Three Machine:  
./replicated-ring-party.x 0 [MPC file name] -pn your-port -h your-server-ip -v \
./replicated-ring-party.x 1 [MPC file name] -pn your-port -h your-server-ip -v \
./replicated-ring-party.x 2 [MPC file name] -pn your-port -h your-server-ip -v 

