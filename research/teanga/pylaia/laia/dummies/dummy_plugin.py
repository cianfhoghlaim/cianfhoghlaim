from pytorch_lightning.plugins import DDPPlugin

import laia.common.logging as log


class DummyLoggingPlugin(DDPPlugin):
    def __init__(self, log_filepath):
        super().__init__()
        self.log_filepath = log_filepath
        self.setup_logging(self.log_filepath)

    @staticmethod
    def setup_logging(log_filepath):
        log.config(fmt="%(message)s", filepath=log_filepath, overwrite=True)

    def __del__(self):
        log.clear()
