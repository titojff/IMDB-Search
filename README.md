Put open_imdb1.nemo_action file on   /.local/share/nemo/actions
Put open_imdb1.py file on            /.local/share/nemo/scripts
make them executable
Check Dependencies:
import os
import re
import sys
import urllib.parse
import urllib.request
import webbrowser
import subprocess
from datetime import datetime



View Debug Log
cat ~/.cache/open_imdb.log
