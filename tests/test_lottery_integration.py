# this is where we're going to actually test on real live chain
# Using Rinkeby as the Ethirium network here.
# --s flag in the terminal is for whatever brownie is going to be print out
import pytest
import time
from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link
from scripts.deploy_lottery import deploy_lottery


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from":account})
    lottery.enter({"from": account, "value":lottery.getEntranceFee()})
    lottery.leave({"from": account, "value":lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from":account})
    # wait for the node to give us a random number
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

    