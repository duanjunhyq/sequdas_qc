# SeqUDAS Quality Control Analysis Component

## Setting up a Development Environment

A conda `environment.yml` file is provided in this repository. It can be used to set up a conda environment as follows:

```
conda env create -f environment.yml
```

Once the environment has been create, activate it:

```
conda activate sequdas-qc
```

...then install the `sequdas_qc` codebase into the environment in 'editable' mode

```
pip install --editable .
```

You can verify that `sequdas-qc` is available on the `$PATH` by invoking the help output as follows:

```
sequdas-qc -h
```
