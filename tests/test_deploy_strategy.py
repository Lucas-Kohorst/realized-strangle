from brownie import reverts


def test_constructor(RealVolStrategy, StrikeSelection, vault, gov, keeper):
    strikeSelection = gov.deploy(
        StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
    strategy = gov.deploy(RealVolStrategy, vault, 2400, 1200, 500, 600, keeper,
                          "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)
    assert strategy.vault() == vault
    assert strategy.pool() == vault.pool()
    assert strategy.baseThreshold() == 2400
    assert strategy.limitThreshold() == 1200
    assert strategy.maxTwapDeviation() == 500
    assert strategy.twapDuration() == 600
    assert strategy.keeper() == keeper
    assert strategy.optionsPremiumPricer() == "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc"


def test_constructor_checks(RealVolStrategy, StrikeSelection, vault, gov, keeper):
    # base_threshold % tickspacing != 0
    with reverts("threshold % tickSpacing"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, 2401, 1200, 500, 600, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)

    # limit_threshold % tickspacing != 0
    with reverts("threshold % tickSpacing"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, 2400, 1201, 500, 600, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)

    # base threshold less than 0
    with reverts("threshold > 0"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, -1, 1200, 500, 600, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)

    # limit threshold less than 0
    with reverts("threshold > 0"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, 2400, -1, 500, 600, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)

    # base threshold greater than pool threshold
    with reverts("threshold too high"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, 1000000, 1200, 500, 600, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)

    # limit threshold greater than pool threshold  
    with reverts("threshold too high"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, 2400, 1000000, 500, 600, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)

    # max_twap_deviation < 0
    with reverts("maxTwapDeviation"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, 2400, 1200, 0, 600, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)

    # twap_duration < 0
    with reverts("twapDuration"):
        strikeSelection = gov.deploy(
            StrikeSelection, "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", 1000, 50)
        strategy = gov.deploy(RealVolStrategy, vault, 2400, 1200, 500, 0, keeper,
                              "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc", strikeSelection.address)
