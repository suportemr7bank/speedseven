"""
Task to run in background
"""

import threading

class BackgroundTask:
    """
        Run tasks in background
    """

    @classmethod
    def exec_callable(cls, _callable, **kwargs):
        """
        Execute a callable in background in saparated process/thread
        """
        thread = threading.Thread(target=_callable, kwargs=kwargs)
        thread.start()
