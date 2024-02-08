#!/bin/bash

ANTLR_JAR="antlr4.jar"

if ! command -v python3 &> /dev/null
then
  apt install python3
  apt install python3-pip
  pip install antlr4-python3-runtime==4.13.1
fi

if ! command -v java &> /dev/null
then
  apt install default-jre
  apt install default-jdk
fi

if [ ! -e "$ANTLR_JAR" ]; then
  curl https://www.antlr.org/download/antlr-4.13.1-complete.jar -o "$ANTLR_JAR"
fi

java -jar $ANTLR_JAR -Dlanguage=Python3 Solidity.g4 -visitor -o sgp/parser/

