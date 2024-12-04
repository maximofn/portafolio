#! /bin/bash

coverage run -m unittest discover -s preparar_notebook/tests -v
coverage report
coverage html