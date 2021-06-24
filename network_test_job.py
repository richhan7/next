"""
network_test_job.py

Example multi-testscript job file

"""
# see https://pubhub.devnetcloud.com/media/pyats/docs/easypy/jobfile.html
# for how job files work

import os
from pyats.easypy import run

# compute the script path from this location
SCRIPT_PATH = os.path.dirname(__file__)


def main(runtime):
    """job file entrypoint"""

    # run script
    run(
        testscript=os.path.join(SCRIPT_PATH, "verify_test.py"),
        runtime=runtime,
        taskid="Device Connections",
    )
