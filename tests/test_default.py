from wake.testing import *

from pytypes.solady.ext.wake.ERC20Mock import ERC20Mock

# Print failing tx call trace
def revert_handler(e: RevertError):
    if e.tx is not None:
        print(e.tx.call_trace)


@chain.connect()
@on_revert(revert_handler)
def test_default():
    owner = chain.accounts[0]
    token = ERC20Mock.deploy("Test Token", "TT", 18)
    mint_erc20(token, owner, 10)
    print("Total supply: ", token.totalSupply())