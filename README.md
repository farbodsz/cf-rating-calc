# cf-rating-calc

Codeforces Rating Calculator for virtual contests.

![screenshot](https://github.com/farbodsz/cf-rating-calc/blob/master/screenshot.png?raw=true)

## Getting Started

First clone the repository and navigate to the project folder:
```bash
$ git clone https://github.com/farbodsz/cf-rating-calc
```

You will need to install Python dependencies. Assuming you're in the project's
root directory containing `requirements.txt`, just do:
```bash
$ pip install -r requirements.txt
```

## Usage

You can calculate your virtual rating by running the Bash script:
```bash
$ ./cfrating.sh 
```

From here, an interactive prompt will guide you to enter the contest ID, points,
etc. Once you're done, your virtual rating change will be calculated.

Alternatively, you can use the main Python script `main.py` which takes 4 
arguments and just outputs a number, the rating change, to `stdout`.
```bash
$ python cf-rating-calc.py <contestId> <points> <penalty> <oldRating>
```

