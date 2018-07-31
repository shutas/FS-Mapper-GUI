# FS-Mapper-GUI

Written by Shuta Suzuki (shutas@umich.edu)

## Overview
There are many scenarios where we want to pair a specific group of data with another group of data by mapping them using a common key.

This is a simple tool that given well-formatted input files and database files (see "Preparation" section for more information), it outputs the mapped version of input files.

## Requirements
#### Normal Users (Recommended):
- `Anaconda` with Python3.x (https://www.anaconda.com/download/)

#### Developers:
- `Python3.x`
- `pip` to install dependencies such as `flask`, `pandas`, etc...
- `git` ...but you probably have it, right? ;)

## Installation
#### Normal Users (Recommended):
Download the source code by clicking on the green `Clone or download` button, then `Download ZIP`.

#### Developers:  
`git clone https://github.com/shutas/FS-Mapper-GUI.git`

## Preparation
There are certain assumptions that this program makes. Here is an ordered list to make sure you're environment is set up before running the program. 

1. Input files should be two-column, tab-delimitted .txt files (NOT .csv FILES!!!) with Unicode encoding. This design decision was made since most of the data on the web cannot be encoded with only ASCII characters. This type of file can be easily created using Microsoft Excel. Simply save the file as `Unicode Text` or `UTF-16 Unicode Text`. Sample input files are located in `sample_input` directory.

2. Similarly, database files should also be two-column, tab-delimitted .txt files (NOT .csv FILES!!!) with Unicode encoding. Sample database files are located in `sample_database` directory.

3. It is assumed that all (and only!) input files are located under the same directory, and all (and only!) database files are located under the another directory.

Input Files Directory Example
```
your_input_directory/  
├── input_file1.txt  
├── input_file2.txt     
└── input_file3.txt    
```

Database Files Directory Example
```
your_database_directory/  
├── database_file1.txt    
└── databatse_file2.txt    
```

4. It is assumed that you have an empty, existing directory for the output files. Anything inside the output directory at runtime WILL BE DELETED COMPLETELY.

Output Files Directory Example (Good)
```
your_output_directory/  
```

Output Files Directory Example (Bad)
```
your_output_directory/  
├── some_file.txt -> Caution: Will be deleted!
└── another_file.txt -> Caution: Will be deleted!
```

## Usage

#### Windows Users
Inside the downloaded folder, there is a batch script named `exe.bat` which will open the program automatically. If this does not work, you may need to change the path to Anaconda3.

#### Mac/Linux Users
In your command line, open the project folder and run:  
`python mapper.py` (Make sure you're using Anaconda3/Python3.x)

Navigate to `localhost:5000` on your favorite browser to open the web application.
