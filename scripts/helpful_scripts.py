from brownie import (
    accounts,
    network, 
    config, 
    VRFCoordinatorMock, 
    MockV3Aggregator, 
    LinkToken, 
    Contract, 
    interface
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def get_account(index=None, id=None):
    # METHODS FOR ADDING ACCOUNTS
    # 1.accounts[0]
    # 2.accounts.add("env")
    # 3.accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if(
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock, 
    "link_token": LinkToken,
}

def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie config
    if defined, Otherwise, it will deploy a mock version of that contract,
    and return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently
            deployed version of this contract. 

    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract

def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("deployind mocks")
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": get_account()})
    print("Mocks Deployed!")

DECIMALS = 8
INITIAL_VALUE=200000000000

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from":account})
    link_token = LinkToken.deploy({"from":account})
    VRFCoordinatorMock.deploy(link_token.address, {"from":account})
    print("Deployed!")

# link token is nothing but link address account
def fund_with_link(contract_address, account=None, link_token=None, amount=250000000000000000): #0.25 Link  
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from":account})
    # we can use the above line or we can use the interface for this funding

    # line 87 or line 91&92 any one option
    
    # using interface getting contract from address token
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from":account})
    tx.wait(1)
    print("Fund Contract!")
    return tx