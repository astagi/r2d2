#!/bin/bash

buildbot stop master
buildslave stop slave

#cat slave/twistd.pid | xargs kill -9