#!/bin/bash
buildbot start master
buildslave start slave
python index.py