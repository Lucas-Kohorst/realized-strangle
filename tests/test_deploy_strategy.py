from brownie import reverts

def test_constructor(RealVolStrategy, vault, gov, keeper):
    strategy = gov.deploy(RealVolStrategy, vault, 2400, 1200, 500, 600, keeper, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
    assert strategy.vault() == vault
    assert strategy.pool() == vault.pool()
    assert strategy.baseThreshold() == 2400
    assert strategy.limitThreshold() == 1200
    assert strategy.maxTwapDeviation() == 500
    assert strategy.twapDuration() == 600
    assert strategy.keeper() == keeper
    assert strategy.optionsPremiumPricer() == "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc"
    assert strategy.delta() == 1000
    assert strategy.step() == 50

def test_constructor_checks(RealVolStrategy, vault, gov, keeper):
    with reverts("threshold % tickSpacing"):
        gov.deploy(RealVolStrategy, vault, 2401, 1200, 500, 600, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)

    with reverts("threshold % tickSpacing"):
        gov.deploy(RealVolStrategy, vault, 2400, 1201, 500, 600, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)

    with reverts("threshold > 0"):
        gov.deploy(RealVolStrategy, vault, 0, 1200, 500, 600, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)

    with reverts("threshold > 0"):
        gov.deploy(RealVolStrategy, vault, 2400, 0, 500, 600, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)

    with reverts("threshold too high"):
        gov.deploy(RealVolStrategy, vault, 887280, 1200, 500, 600, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)

    with reverts("threshold too high"):
        gov.deploy(RealVolStrategy, vault, 2400, 887280, 500, 600, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)

    with reverts("maxTwapDeviation"):
        gov.deploy(RealVolStrategy, vault, 2400, 1200, -1, 600, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)

    with reverts("twapDuration"):
        gov.deploy(RealVolStrategy, vault, 2400, 1200, 500, 0, keeper,
                   "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
