#!/bin/bash

pip3 install Flask
pip3 install html5lib
pip3 install bs4
mv _baidu.py src/baidu.py
nano src/baidu.py
cd src
python3 app.py