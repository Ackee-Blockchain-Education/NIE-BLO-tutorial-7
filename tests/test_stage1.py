import logging

from wake.testing import *
from wake.testing.fuzzing import *

from pytypes.contracts.stage1.NumberMagic import NumberMagic


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Print failing tx call trace
def revert_handler(e: TransactionRevertedError):
    if e.tx is not None:
        logger.debug(e.tx.call_trace)


class NumberMagicFuzzTest(FuzzTest):

    def pre_sequence(self) -> None:
        self.nm = NumberMagic.deploy()
        logger.debug(f"Starting sequence")

    def _rand(self) -> int256:
        # try `random_int(-(10**6), 10**6)` for faster fuzzing
        return random_int(-int256.min, int256.max)

    @flow()
    def flow_multiply(self):
        n = self._rand()
        self.nm.multiply(n)
        logger.debug(f"multiply({n})")

    @flow()
    def flow_divide(self):
        n = self._rand()
        self.nm.divide(n)
        logger.debug(f"divide({n})")

    @flow()
    def flow_xor(self):
        n = self._rand()
        self.nm.xor(n)
        logger.debug(f"xor({n})")

    @invariant()
    def invariant_isLocked(self):
        assert self.nm.isLocked()


@default_chain.connect()
@on_revert(revert_handler)
def test_stage1():
    NumberMagicFuzzTest().run(sequences_count=10, flows_count=100)
