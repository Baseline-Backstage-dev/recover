# Recover
Document processing

## Local development 

### Installation
To install the package and pre-commit hook, run:
```commandline
make install
make install_precom
```
The pre-commit by default contains the following hooks: Black, Flake8, iSort and Mypy.

### Linting and testing
For linting, run:
```commandline
make lint
```
This runs them with the same setup as the pre-commit does.

To run the tests:
```
make test
```

### Deployment
To deploy the stack locally, run the following two commands:
```commandline
make localstack
```
In a different terminal:
```commandline
make deploy
```
If you want to have pulumilocal keep update your AWS resources while you change them, use:
```commandline
make watch
```
Do take into account that this doesn't update your lambda layer that contains all code under `domain/`. 
If you make changes to the domain-specific code and would like to see them in action in localstack, run:
```commandline
make destroy
make deploy
```

### Other
For other useful commands check `make help`.

## AWS
### Development
For AWS development, the makefile `Makefile.aws.mk` is used. To check all the different commands, run:
```commandline
make -f Makefile.aws.mk help
```
To deploy your stack:
```commandline
make -f Makefile.aws.mk deploy
```
To destroy the resources and stack:
```commandline
make -f Makefile.aws.mk destroy
```
**NB: make sure to destroy the resources to avoid unnecessary costs!**
