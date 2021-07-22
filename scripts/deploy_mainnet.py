from brownie import accounts, ZERO_ADDRESS, AlphaVault, RealVolStrategy, StrikeSelection
from brownie.network.gas.strategies import GasNowScalingStrategy

POOL = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"  # USDC / ETH / 0.3%
# POOL = "0x4e68ccd3e89f51c3074ca5072bbac773960dfa36"  # ETH / USDT / 0.3%

PROTOCOL_FEE = 5000  # 5%
MAX_TOTAL_SUPPLY = 2e17
BASE_THRESHOLD = 3600
LIMIT_THRESHOLD = 1200
PERIOD = 43200  # 12 hours
MIN_TICK_MOVE = 0
MAX_TWAP_DEVIATION = 100  # 1%
TWAP_DURATION = 60  # 60 seconds
KEEPER = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" ## address for testing @TOODO change for deployment
OPTIONS_PREMIUM_PRICER = "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc"
DELTA = 1000
STEP = 50
STRIKE_SELECTION = ZERO_ADDRESS

def main():
    deployer = accounts[10] # wallet added in to brownie-config for mock testing
    balance = deployer.balance()

    gas_strategy = GasNowScalingStrategy()

    ## deploy strike selection
    print(
        f"""
        StrikeSelection Strategy Parameters
        OPTIONS_PREMIUM_PRICER:  {OPTIONS_PREMIUM_PRICER}
        DELTA: '{DELTA}'
        STEP:  {STEP}
    """
    )

    if input("Deploy StrikeSelection? y/[N]: ").lower() != "y":
        return

    strikeSelection = deployer.deploy(
        StrikeSelection,
        OPTIONS_PREMIUM_PRICER,
        DELTA,
        STEP,
        gas_price=gas_strategy,
    )

    ## set strike selection address
    STRIKE_SELECTION = strikeSelection.address     

    ## deploy vault
    print(
        f"""
        Vault Strategy Parameters
        POOL:  {POOL}
        PROTOCOL_FEE:  {PROTOCOL_FEE}
        MAX_TOTAL_SUPPLY: '{MAX_TOTAL_SUPPLY}'
    """
    )
    
    if input("Deploy Vault? y/[N]: ").lower() != "y":
        return

    vault = deployer.deploy(
        AlphaVault,
        POOL,
        PROTOCOL_FEE,
        MAX_TOTAL_SUPPLY,
        gas_price=gas_strategy,
    )

    ## deploy strategy
    print(
        f"""
        RealVol Strategy Parameters
        RealVolStrategy:  {RealVolStrategy}
        Vault:  {vault}
        BASE_THRESHOLD: '{BASE_THRESHOLD}'
        LIMIT_THRESHOLD: '{LIMIT_THRESHOLD}'
        PERIOD: '{PERIOD}'
        MIN_TICK_MOVE: '{MIN_TICK_MOVE}'
        MAX_TWAP_DEVIATION: '{MAX_TWAP_DEVIATION}'
        KEEPER: '{KEEPER}',
        OPTIONS_PREMIUM_PRICER: '{OPTIONS_PREMIUM_PRICER}',
        STRIKE_SELECTION: '{STRIKE_SELECTION}'
    """
    )

    if input("Deploy Strategy? y/[N]: ").lower() != "y":
        return

    strategy = deployer.deploy(
        RealVolStrategy,
        vault,
        BASE_THRESHOLD,
        LIMIT_THRESHOLD,
        MAX_TWAP_DEVIATION,
        TWAP_DURATION,
        KEEPER,
        OPTIONS_PREMIUM_PRICER,
        STRIKE_SELECTION,
        gas_price=gas_strategy,
    )   

    vault.setStrategy(strategy, {"from": deployer, "gas_price": gas_strategy})