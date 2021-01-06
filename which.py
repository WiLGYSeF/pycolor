import os
import subprocess


def which(name):
    try:
        output = subprocess.check_output([
            'where' if os.name == 'nt' else 'which',
            name
        ])
        return output[:-1] if output[-1] == ord('\n') else output
    except subprocess.CalledProcessError as cpe:
        if cpe.returncode == 1:
            return None
