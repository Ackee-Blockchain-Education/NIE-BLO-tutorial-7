import logging

from wake.testing import *
from wake.testing.fuzzing import *

from pytypes.contracts.stage2.FaultyStakes import FaultyStakes


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Print failing tx call trace
def revert_handler(e: TransactionRevertedError):
    if e.tx is not None:
        logger.debug(e.tx.call_trace)


class FaultyStakesFuzzTest(FuzzTest):

    fs: FaultyStakes
    owner: Account
    stakers: List[Account]

    STAKE_AMOUNT: Wei = Wei.from_ether(0.5)
    UNSTAKE_AMOUNT = Wei.from_ether(0.1)
    WITHDRAW_AMOUNT = Wei.from_ether(0.05)
    WRONG_ANSWER_PROB = 0.5

    def pre_sequence(self) -> None:
        self.owner = default_chain.accounts[0]
        self.stakers = default_chain.accounts[1:6]
        self.fs = ...

        logger.debug(f"Starting sequence")

    def post_flow(self, _):
        # mine a block with random delay from the current time
        default_chain.mine(lambda t: t + random_int(0, 100))

    @flow()
    def flow_stake(self):
        pass

    @flow(weight=1000)
    def flow_play(self):
        player = random.choice(self.stakers)
        ts = default_chain.blocks["pending"].timestamp
        correct_answer = ts % 100
        will_answer_correctly = random.random() > self.WRONG_ANSWER_PROB
        # Add 1 to the correct answer with probability WRONG_ANSWER_PROB
        answer = correct_answer + int(not will_answer_correctly)

        with may_revert(FaultyStakes.NotEnoughStake):
            pass

    @flow()
    def flow_unstake(self):
        pass

    @flow()
    def flow_withdraw(self):
        pass


@default_chain.connect()
@on_revert(revert_handler)
def test_stage2():
    chain.tx_callback = lambda tx: (
        logger.debug(tx.console_logs) if tx.console_logs else None
    )
    FaultyStakesFuzzTest().run(sequences_count=1, flows_count=1000)
