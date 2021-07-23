from brownie import reverts, ZERO_ADDRESS
import pytest
from pytest import approx

# assert approx(total1After) == total1
# PROTOCOL_FEE = 5000  # 5%
# MAX_TOTAL_SUPPLY = 2e17
# BASE_THRESHOLD = 3600
# LIMIT_THRESHOLD = 1200
# PERIOD = 43200  # 12 hours
# MIN_TICK_MOVE = 0
# MAX_TWAP_DEVIATION = 100  # 1%
# TWAP_DURATION = 60  # 60 seconds
# # address for testing @TOODO change for deployment
# KEEPER = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
# OPTIONS_PREMIUM_PRICER = "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc"
# DELTA = 1000
# STEP = 50
# STRIKE_SELECTION = ZERO_ADDRESS # test strikeselection deployment address

def test_getStrikePriceAsTicks(
    gov,
    RealVolStrategy,
    StrikeSelection,
    vault):

    # set up
    # deploy StrikeSelection
    strikeSelection = gov.deploy(
        StrikeSelection,
        "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc",
        1000,
        50
    )

    strategy = gov.deploy(
        RealVolStrategy,
        vault,
        3600,
        1200,
        100,
        60,
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc",
        strikeSelection.address
    )
    
    # check that the strike is around a .1delta
    (put_tick, put_strike, put_delta) = strategy.getPutStrikePriceAsTicks()
    (call_tick, call_strike, call_delta) = strategy.getCallStrikePriceAsTicks()

    put_delta = 1 - (put_delta / 10000)
    call_delta = call_delta / 10000

    print(put_delta)
    print(call_delta)

    ## checking that the delta is within the expected range
    assert put_delta <= .125 and put_delta >= .075
    assert call_delta <= .125 and call_delta >= .075
