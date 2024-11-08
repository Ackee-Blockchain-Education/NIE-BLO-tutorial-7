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
        self.fs = FaultyStakes.deploy(from_=self.owner)

        logger.debug(f"Starting sequence")

    def post_flow(self, _):
        # mine a block with random delay from the current time
        default_chain.mine(lambda t: t + random_int(0, 100))

    @flow()
    def flow_stake(self):
        staker = random.choice(self.stakers)
        stake = random_int(0, self.STAKE_AMOUNT)
        self.fs.stake(value=stake, from_=staker)
        logger.debug(f"stake({stake}, from={staker})")

    @flow(weight=1000)
    def flow_play(self):
        player = random.choice(self.stakers)
        ts = default_chain.blocks["pending"].timestamp
        correct_answer = ts % 100
        will_answer_correctly = random.random() > self.WRONG_ANSWER_PROB
        # Add 1 to the correct answer with probability WRONG_ANSWER_PROB
        answer = correct_answer + int(not will_answer_correctly)

        with may_revert(FaultyStakes.NotEnoughStake):
            self.fs.play(answer, from_=player)
            logger.debug(
                f"play({answer}, from={player}) (correct={will_answer_correctly})"
            )

    @flow()
    def flow_unstake(self):
        staker = random.choice(self.stakers)
        unstake = random_int(0, self.UNSTAKE_AMOUNT)
        with may_revert((FaultyStakes.InsufficientStake, FaultyStakes.TooManyUnstakes)):
            self.fs.unstake(unstake, from_=staker)
            logger.debug(f"unstake({unstake}, from={staker})")

    @flow()
    def flow_withdraw(self):
        staker = random.choice(self.stakers)
        withdraw = random_int(0, self.WITHDRAW_AMOUNT)
        day_passed = random_bool(true_prob=0.7)
        if day_passed:
            default_chain.mine(lambda t: t + 10000)
        with may_revert(
            (FaultyStakes.UnstakeNotAvailable, FaultyStakes.InsufficientValueLocked)
        ):
            self.fs.withdraw(withdraw, from_=staker)
            logger.debug(
                f"withdraw({withdraw}, from={staker}) (delay passed: {day_passed})"
            )


@default_chain.connect()
@on_revert(revert_handler)
def test_stage2():
    chain.tx_callback = lambda tx: (
        logger.debug(tx.console_logs) if tx.console_logs else None
    )
    FaultyStakesFuzzTest().run(sequences_count=1, flows_count=1000)
