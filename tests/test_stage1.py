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
        pass

    # @flow()
    # def ...

    # @invariant()
    # def ...


@default_chain.connect()
@on_revert(revert_handler)
def test_stage1():
    NumberMagicFuzzTest().run(sequences_count=10, flows_count=100)
