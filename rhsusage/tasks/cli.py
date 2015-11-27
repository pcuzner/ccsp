__author__ = 'paul'

import threading
import subprocess
import os
import signal


class ShellCommand(object):

    def __init__(self, cmd, timeout=1):
        self.cmd = cmd
        self.cmdProcess = None
        self.timeout = timeout
        self.rc = 0  # -1 ... timeout
        # 0 .... successful
        # n .... RC from command

        self.stdout = []
        self.stderr = []

    def run(self):
        """ Run the command inside a thread to enable a timeout to be
            assigned """

        def command_thread():
            """ invoke subprocess to run the command """

            self.cmdProcess = subprocess.Popen(self.cmd,
                                               shell=True,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               preexec_fn=os.setsid)

            stdout, stderr = self.cmdProcess.communicate()
            self.stdout = stdout.split('\n')[:-1]
            self.stderr = stderr.split('\n')[:-1]

        thread = threading.Thread(target=command_thread)
        thread.start()

        thread.join(self.timeout)

        if thread.is_alive():
            os.killpg(self.cmdProcess.pid, signal.SIGTERM)
            self.rc = -1
        else:
            # the thread completed normally
            self.rc = self.cmdProcess.returncode