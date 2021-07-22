# import {ethers} from "hardhat"
# import {assert
#         import expect} from "chai"
# import {Contract} from "@ethersproject/contracts"
# import * as time from "./helpers/time"
# import {BigNumber} from "@ethersproject/bignumber"
# import {SignerWithAddress} from "@nomiclabs/hardhat-ethers/signers"

# const {getContractFactory} = ethers

# describe("StrikeSelection", ()= > {
#     let strikeSelection: Contract
#     let mockOptionsPremiumPricer: Contract
#     let mockPriceOracle: Contract
#     let mockVolatilityOracle: Contract
#     let signer: SignerWithAddress
#     let signer2: SignerWithAddress

#     before(async function() {
#         [signer, signer2]=await ethers.getSigners()
#         const MockOptionsPremiumPricer=await getContractFactory(
#             "MockOptionsPremiumPricer",
#             signer
#         )
#         const MockPriceOracle=await getContractFactory("MockPriceOracle", signer)
#         const MockVolatilityOracle=await getContractFactory(
#             "MockVolatilityOracle",
#             signer
#         )
#         const StrikeSelection=await getContractFactory("StrikeSelection", signer)

#         mockOptionsPremiumPricer=await MockOptionsPremiumPricer.deploy()

#         mockPriceOracle=await MockPriceOracle.deploy()
#         mockVolatilityOracle=await MockVolatilityOracle.deploy()

#         await mockOptionsPremiumPricer.setPriceOracle(mockPriceOracle.address)
#         await mockOptionsPremiumPricer.setVolatilityOracle(
#             mockVolatilityOracle.address
#         )
#         await mockOptionsPremiumPricer.setPool(mockPriceOracle.address)
#         await mockPriceOracle.setDecimals(8)
#         await mockVolatilityOracle.setAnnualizedVol(1)

#         await mockOptionsPremiumPricer.setOptionUnderlyingPrice(
#             BigNumber.from(2500).mul(
#                 BigNumber.from(10).pow(await mockPriceOracle.decimals())
#             )
#         )

#         strikeSelection=await StrikeSelection.deploy(
#             mockOptionsPremiumPricer.address,
#             1000,
#             100
#         )
#     })

#     describe("setDelta", ()=> {
#     })

#     describe("setStep", ()=> {
#     })

#     describe("getStrikePrice", ()=> {
#     })

    
# })
