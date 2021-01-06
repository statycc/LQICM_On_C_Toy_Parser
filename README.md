# Loop Quasi-Invariant Chunk Motion

This is a pass which computes the invariance degree of each statement
in loops and inner loops in a way to peel them.

With a relation composition, it is able to hoist an entire invariant or
quasi-invariant inner loop.

## Prerequisites 

This uses the [pycparser](https://github.com/eliben/pycparser).

Install project dependencies by running the following command:

```text
python -m pip install -r requirements.txt
```


## Installation 

Install [pycparser](https://github.com/eliben/pycparser).

Run on examples:

    $ python LQICM.py yourfile.c

Example:

    $ python LQICM.py c_files/example2.c

Remark:

The `.c` file given needs to contain only functions (no
`includes` or other macros etc…)
