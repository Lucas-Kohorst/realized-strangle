## Realized Strangle
Open a perpetual strangle (selling a put at a lower strike and a call at a higher strike) position on Uniswap V3 to sell realized volatility and capture fees. 

This repository contains the smart contracts from the [Alpha Vaults](https://alpha.charm.fi/) protocol and leverages [ribbon.finanace rvol](https://github.com/ribbon-finance/rvol).

### TODO 
- [ ] Add Testing 
- [ ] Emit rebalance events

### Recomended Reading
- [Uniswap V3 LP Tokens as Perpetual Put and Call Options](https://lambert-guillaume.medium.com/uniswap-v3-lp-tokens-as-perpetual-put-and-call-options-5b66219db827)
- [Synthetic Options and Short Calls in Uniswap V3](https://lambert-guillaume.medium.com/synthetic-options-and-short-calls-in-uniswap-v3-a3aea5e4e273)
- [Rebalancing vs Passive strategies for Uniswap V3 liquidity pools](https://medium.com/@DeFiScientist/rebalancing-vs-passive-strategies-for-uniswap-v3-liquidity-pools-754f033bdabc)
- [Uniswap V3: A Quant Framework to model yield farming returns](https://medium.com/@DeFiScientist/uniswap-v3-a-quant-framework-to-model-yield-farming-returns-941a1600425e)

### Usage

Before compiling, run below. The uniswap-v3-periphery package has to be cloned
otherwise imports don't work.

`brownie pm clone Uniswap/uniswap-v3-periphery@1.0.0`

Run tests

`brownie test`

Run tests with with coveragee
`brownie test -s --coverage`

To deploy, modify the parameters in `scripts/deploy_mainnet.py` and run:

`brownie run deploy_mainnet`

To trigger a rebalance, run:

`brownie run rebalance`

### Testing

#### Experimenting with Brownie and Vol Oracle
 
```
## starting up 
brownie console --network mainnet

oracle = Contract.from_explorer("0x8eB47e59E0C03A7D1BFeaFEe6b85910Cefd0ee99")
pricer = Contract.from_explorer("0x966878c047e3e4aDa52Baa93A94bc176FF67b2Dc")

pricer.getOptionDelta(250000000000, 1627160535) / 10000 ## get option delta ex: 8100 = 0.81 delta)

oracle.twap("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8") / 10**18 ## USDC for ETH
1 / (oracle.twap("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8") / 10**18) * 1.2 ## x% rise in price converted to ETH to usdc pair
```

#### Deploy Contracts
```
run("deploy_mainnet")
strike = Contract.from_abi("Strike", "0xeC859E8966E83a11a535d452dcFDFc51504Af9F9", StrikeSelection.abi)
real = Contract.from_abi("RealVolStrat", "0xecAF80dE71c980886870F615b6933dC971A94AfA", RealVolStrategy.abi)

current_tick = real.getTick()
## call price
(call_price, call_delta) = strike.getStrikePrice(1627616181, False)
call_price = call_price * 1e22
call_tick = real.testTick(call_price)

## put price
(put_price, put_delta) = strike.getStrikePrice(1627616181, True)
put_price = put_price * 1e22
put_tick = real.testTick(put_price)

put_price = real.testPrice(put_tick) ## check sqrtPriceX96
current_price = real.testPrice(current_tick)
call_price = real.testPrice(call_tick) ## check sqrtPriceX96

# print strike, tick, and deltas
print('put_price={:f}, put_delta={:f}, put_tick={:f}\n current_price={:f}, current_tick={:f}\n call_price={:f},call_delta={:f}, call_tick={:f}'.format(
  put_price / 1e30, 
  1 - (put_delta / 10000), 
  put_tick,
  current_price / 1e30,
  current_tick,
  call_price / 1e30, 
  call_delta / 10000,
  call_tick
))
```

```
run("deploy_mainnet")
strike = Contract.from_abi("Strike", "0xeC859E8966E83a11a535d452dcFDFc51504Af9F9", StrikeSelection.abi)
real = Contract.from_abi("RealVolStrat", "0xecAF80dE71c980886870F615b6933dC971A94AfA", RealVolStrategy.abi)
real.getPutStrikePriceAsTicks()
real.getCallStrikePriceAsTicks()
```

#### Calculating vault rebalances
```
tickFloor - real.baseThreshold() # lower
tickCeil + real.baseThreshold()  # upper

# getting ticks
(put,tick, put_strike, put_expiry) = real.getPutStrikePriceAsTicks() 
lowerThreshold = put_tick # lower
(call_tick, call_strike, call_expiry) = real.getCallStrikePriceAsTicks()
upper_threshold = call_tick # upper

## testing a rebalance
real.rebalance({'from': '0xd8da6bf26964af9d7eed9e03e53415d37aa96045'}) # w/ the keeper addr for now unlocked in brownie-config.yaml
```
