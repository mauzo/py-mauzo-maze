#!/bin/sh

set -ex

cc -c -o glad.o src/glad.c -Iinclude
cc -c -o gltest.o gltest.c -Iinclude -I/usr/local/include
cc -o gltest gltest.o glad.o -L/usr/local/lib -lglfw
