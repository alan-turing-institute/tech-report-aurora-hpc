## Technical Report

This directory contains the technical report that details the work and the results which followed from it.

Building a PDF from the sourced requires a TeXLive installation with XeLaTeX, as well the Euler Math and CMU Fonts to be installed.

On Ubuntu, this can be achieved as follows:

```
$ sudo apt install build-essential
$ sudo apt install latexmk xelatex texlive-xetex texlive-bibtex-extra biber
$ sudo apt install fonts-cmu texlive-fonts-extra
```

Once installed the document can be built as follows:

```
$ cd aurora-hpc/documents/tech-report
$ make
```

If all goes to plan, the resulting document will be called `tech-report-aurora-dawn.pdf`.
To delete this and all other generated files, run the following:

```
$ make clean
```

