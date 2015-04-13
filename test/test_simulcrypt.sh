#!/bin/sh

python2 ../src/CodeDependencyVisualizer.py -aiptP --verbose -d "${RES_DIR}/Software/Resources/Simulcrypt/ECMSubsystem" -I "${RES_DIR}/Software/" && dot -T svg -o uml.svg uml.dot && firefox uml.svg
