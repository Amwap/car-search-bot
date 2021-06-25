import  subprocess
try:
    from bot import *
finally:
    subprocess.Popen(['python3.9', 'run.py', '&'])