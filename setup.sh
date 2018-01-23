#!/usr/bin/env bash
#brew install libusb
#brew install openssl && brew install swig
#LDFLAGS="-L$(brew --prefix openssl)/lib" \
#CFLAGS="-I$(brew --prefix openssl)/include" \
#SWIG_FEATURES="-I$(brew --prefix openssl)/include" \
# pip install m2crypto

pip3 install pipenv
pipenv --three
pipenv install
pipenv shell