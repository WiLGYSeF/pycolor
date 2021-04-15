import os
import subprocess


def which(name):
    try:
        if os.name == 'nt':
            cmd = [ 'where', name ]
        else:
            cmd = [ 'which', '--', name ]

        output = subprocess.check_output(cmd)
        return output[:-1] if output[-1] == ord('\n') else output
    except subprocess.CalledProcessError as cpe:
        if cpe.returncode == 1:
            return None
        raise cpe
