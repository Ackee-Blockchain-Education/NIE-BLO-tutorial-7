# NIE-BLO Tutorial 7
This repository contains [Solady](https://github.com/Vectorized/solady/tree/2af06408b6a204824c2ecb245779ed400b535fb5) repository as a submodule. The project serve for exploration of more advanced auditing techniques, e.g. static analysis and fuzz testing.


## Setup

1. Clone this repository
2. `git submodule update --init --recursive` if not cloned with `--recursive`

## Running Wake

1. `wake up pytypes` to generate pytypes
2. `wake test` to test the project once you create some tests
3. `wake init detector foo` to initialize the empty detector called `foo`
4. `wake init printer bar` to initialize the empty printer called `bar`
