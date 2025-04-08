# Clause2Inv

Clause2Inv, LLM clause generator and clause combination algorithm.

## Table of Contents

- [Installation and Setup](#installation-and-setup)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Example](#example)
- [Contributing](#contributing)

## Installation and Setup

### Prerequisites

- **Python Version**: 3.8
- **Dependencies**: The following Python libraries are required:
  - numpy
  - openai
  - pandas
  - pyjson5
  - rich
  - scikit-learn
  - scipy
  - socksio
  - tqdm
  - z3-solver

Install all dependencies with:

```bash
conda env create -f env.yml
```

## Project Structure

```
Clause2Inv/
│
├── README.md               	# readme
├── env.yml                	# conda env file
├── generator/                	# LLM
└── combinator/                 # Algorithm
    ├── linear.sh          	# Run linear problem
    ├── run_linear.py         	# Run linear benchmark
    ├── checker.py      	# Algorithm detail
    ├── output_linear/          # Output files
    └── ...          		# Other files
```

## Usage

### Running the Main Program

Ensure you're in the project's clause2inv/combinator directory, then execute the first problem of linear benchmark as follows:

```bash
./linear 1
```

## Example

Below is an example command to run the linear benchmark:

```bash
python run_linear.py
```

## Contributing

We welcome contributions! Feel free to submit pull requests or contact the project maintainers with suggestions.
