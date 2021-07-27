# msci-541-720-hw4-christinajiyunlee

## MSCI 541 Homework 4
###### Christina (Jiyun) Lee


### Languages Used
Python3 was the language used to build the program. 

### How to Run & Build Program
#### ComputeAverages.py
1.	Download the `hw3-files-2021` folder into the root directory of the project.
2.	Open the command line
3.	Navigate to the root directory of the project `../msci-541-720-hw3-christinajiyunlee`
4.	Run `ComputeAverages.py` by entering the following command: `python ComputeAverages.py`
5.	If run successfully, you should now see the formatted outputs of topic averages for student2 & student 12 (`student2_output.txt` & `student12_output.txt`), csv of mean averages (`hw3-5a-J623LEE.csv`) and a csv of student's t-test p-values (`hw3-5d-J623LEE.csv`) in the root directory of the project.

#### BM25.py
1. Ensure `avdl.txt` file contains numeric value of the average length of all documents in collection
2. Open the command line
3. Navigate to the root directory of the project `../msci-541-720-hw4-christinajiyunlee`
4. Run `BM25.py` by entering the following command: `python BM25.py`
5. If run successfully, you should see either the `hw4-bm25-baseline-j623lee.txt` or `hw4-bm25-stem-j623lee.txt` file in the root directory of the project, depending on the configuration of the script. 

#### BooleanAND.py
This file does not need to be run, as it is imported into the `BM25.py` file and used there.
                                                             
#### ComputeAverages.py
1.	Generate the `hw4-bm25-baseline-j623lee.txt`, `hw4-bm25-stem-j623lee.txt` files into the root directory of the project.
2.	Open the command line
3.	Navigate to the root directory of the project `../msci-541-720-hw4-christinajiyunlee`
4.	Run `ComputeAverages.py` by entering the following command: `python ComputeAverages.py`
5.	If run successfully, you should now see the formatted outputs in the `hw4-metrics-j623lee.txt` file

#### IndexEngine.py
1.	Download the `latimes.gz` compressed file into the root directory of the project
2.	Open the command line
3.	Navigate to the root directory of the project `../msci-541-720-hw4-christinajiyunlee`
4.	Run `IndexEngine.py` by entering the following command: `python IndexEngine.py latimes.gz latimes-index`
5.	If you see an `ERROR`, follow the instructions to resolve then run the command from step 4 again
6.	If run successfully, you should now see an `latimes-index/` directory and `index.txt` file in the root directory of the project.

#### PorterStemmer.py
This script was optained from https://tartarus.org/martin/PorterStemmer/.
It was written by `Vivake Gupta`, following the algorithm from `Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14, no. 3, pp 130-137,` and was available as open source code.
       