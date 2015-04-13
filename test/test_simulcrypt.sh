#!/bin/sh

python2 ../src/CodeDependencyVisualizer.py -aiptP --verbose -d ${RES_DIR}/Resources/Simulcrypt/ECMSubsystem -I ${RES_DIR}/ && dot -T svg -o uml.svg uml.dot && firefox uml.svg
