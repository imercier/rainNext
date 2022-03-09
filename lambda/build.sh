#! /bin/bash
pigar -c requirements.txt
pip install --target ./package -r requirements.txt  --upgrade
rm -f my-deployment-package.zip
cd package
zip -q -r ../my-deployment-package.zip .
cd ..
zip -q -g my-deployment-package.zip rainNext.py

