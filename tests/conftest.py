from brownie import chain
from math import sqrt
import pytest
from web3 import Web3

UNISWAP_V3_CORE = "Uniswap/uniswap-v3-core@1.0.0"

@pytest.fixture
def gov(accounts):
    yield accounts[0]


@pytest.fixture
def user(accounts):
    yield accounts[1]


@pytest.fixture
def recipient(accounts):
    yield accounts[2]


@pytest.fixture
def keeper(accounts):
    # yield accounts[3]
    yield "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


@pytest.fixture
def users(gov, user, recipient, keeper):
    yield [gov, user, recipient, keeper]


@pytest.fixture
def router(TestRouter, gov):
    yield gov.deploy(TestRouter)


@pytest.fixture
def pool(MockToken, router, pm, gov, users):
    UniswapV3Core = pm(UNISWAP_V3_CORE)

    tokenA = gov.deploy(MockToken, "name A", "symbol A", 18)
    tokenB = gov.deploy(MockToken, "name B", "symbol B", 18)
    fee = 3000

    factory = gov.deploy(UniswapV3Core.UniswapV3Factory)
    tx = factory.createPool(tokenA, tokenB, fee, {"from": gov})
    pool = UniswapV3Core.interface.IUniswapV3Pool(tx.return_value)
    token0 = MockToken.at(pool.token0())
    token1 = MockToken.at(pool.token1())

    # initialize price to 100
    price = int(sqrt(100) * (1 << 96))
    pool.initialize(price, {"from": gov})

    for u in users:
        token0.mint(u, 100e18, {"from": gov})
        token1.mint(u, 10000e18, {"from": gov})
        token0.approve(router, 100e18, {"from": u})
        token1.approve(router, 10000e18, {"from": u})

    # Add some liquidity over whole range
    max_tick = 887272 // 60 * 60
    router.mint(pool, -max_tick, max_tick, 1e16, {"from": gov}) 

    # Increase cardinality and fast forward so TWAP works
    pool.increaseObservationCardinalityNext(100, {"from": gov})
    chain.sleep(3600)
    yield pool


@pytest.fixture
def tokens(MockToken, pool):
    return MockToken.at(pool.token0()), MockToken.at(pool.token1())

@pytest.fixture
def vault(AlphaVault, RealVolStrategy, pool, router, tokens, gov, users, keeper):
    # protocolFee = 10000 (1%)
    # maxTotalSupply = 100e18 (100 tokens)
    vault = gov.deploy(AlphaVault, pool, 10000, 100e18)

    for u in users:
        tokens[0].approve(vault, 100e18, {"from": u})
        tokens[1].approve(vault, 10000e18, {"from": u})

    # baseThreshold = 2400
    # limitThreshold = 1200
    # maxTwapDeviation = 200000 (just a big number)
    # twapDuration = 600 (10 minutes)
    # strategy = gov.deploy(RealVolStrategy, vault, 2400, 1200, 500, 600,
    #                       keeper, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
    # vault.setStrategy(strategy, {"from": gov})

    yield vault


@pytest.fixture
def strategy(RealVolStrategy, vault):
    return RealVolStrategy.at(vault.strategy())


@pytest.fixture
def vaultAfterPriceMove(vault, strategy, pool, router, gov, keeper):

    # Deposit and move price to simulate existing activity
    vault.deposit(1e16, 1e18, 0, 0, gov, {"from": gov})
    prevTick = pool.slot0()[1] // 60 * 60
    router.swap(pool, True, 1e16, {"from": gov})

    # Check price did indeed move
    tick = pool.slot0()[1] // 60 * 60
    assert tick != prevTick

    # Rebalance vault
    strategy.rebalance({"from": keeper})

    # Check vault holds both tokens
    total0, total1 = vault.getTotalAmounts()
    assert total0 > 0 and total1 > 0

    yield vault


@pytest.fixture
def vaultOnlyWithToken0(vault, strategy, pool, router, gov, keeper):

    # Deposit
    vault.deposit(1e14, 1e16, 0, 0, gov, {"from": gov})

    # Rebalance vault
    strategy.rebalance({"from": keeper})

    # Swap token0 -> token1
    router.swap(pool, True, 1e16, {"from": gov})

    # Check vault holds only token0
    total0, total1 = vault.getTotalAmounts()
    assert total0 > 0
    assert total1 == 0

    yield vault


@pytest.fixture
def vaultOnlyWithToken1(vault, strategy, pool, router, gov, keeper):

    # Deposit
    vault.deposit(1e14, 1e16, 0, 0, gov, {"from": gov})

    # Rebalance vault
    strategy.rebalance({"from": keeper})

    # Swap token1 -> token0
    router.swap(pool, False, 1e18, {"from": gov})

    # Check vault holds only token0
    total0, total1 = vault.getTotalAmounts()
    assert total0 == 0
    assert total1 > 0

    yield vault


@pytest.fixture
def poolFromPrice(pm, AlphaVault, MockToken, tokens, gov):
    def f(price):
        UniswapV3Core = pm(UNISWAP_V3_CORE)
        fee = 3000

        factory = gov.deploy(UniswapV3Core.UniswapV3Factory)
        tx = factory.createPool(tokens[0], tokens[1], fee, {"from": gov})
        pool = UniswapV3Core.interface.IUniswapV3Pool(tx.return_value)
        pool.initialize(price, {"from": gov})

        # Increase cardinality and fast forward so TWAP works
        pool.increaseObservationCardinalityNext(100, {"from": gov})
        chain.sleep(3600)
        return pool

    yield f


@pytest.fixture
def getPositions(pool):
    def f(vault):
        baseKey = computePositionKey(vault, vault.baseLower(), vault.baseUpper())
        limitKey = computePositionKey(vault, vault.limitLower(), vault.limitUpper())
        return pool.positions(baseKey), pool.positions(limitKey)

    yield f


@pytest.fixture
def debug(pool, tokens):
    def f(vault):
        baseKey = computePositionKey(vault, vault.baseLower(), vault.baseUpper())
        limitKey = computePositionKey(vault, vault.limitLower(), vault.limitUpper())
        print(f"Passive position:    {pool.positions(baseKey)}")
        print(f"Rebalance position:  {pool.positions(limitKey)}")
        print(f"Spare balance 0:  {tokens[0].balanceOf(vault)}")
        print(f"Spare balance 1:  {tokens[1].balanceOf(vault)}")

    yield f


def computePositionKey(owner, tickLower, tickUpper):
    return Web3.solidityKeccak(
        ["address", "int24", "int24"], [str(owner), tickLower, tickUpper]
    )
