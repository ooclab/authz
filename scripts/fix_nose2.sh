#!/bin/bash

RESULT_PATH=$(python3 -c 'import os, nose2; print(os.path.join(os.path.dirname(nose2.__file__), "plugins/result.py"))')
# support sed in linux and macos
sed -e 's@desc = .*doc_first_line.*@desc = doc_first_line@' ${RESULT_PATH} > /tmp/_result.py
mv /tmp/_result.py ${RESULT_PATH}
