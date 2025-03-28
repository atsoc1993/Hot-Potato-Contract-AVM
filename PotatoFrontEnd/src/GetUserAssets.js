import { AlgorandClient } from "@algorandfoundation/algokit-utils";


const getUserAssets = async (address) => {

    const algorand = AlgorandClient.testNet()

    const userAssets = []
    const userAssetsInfo = (await algorand.client.algod.accountInformation(address).do()).assets
    for (const asset of userAssetsInfo) {
        userAssets.push({
            assetId: BigInt(asset.assetId), 
            assetAmount: BigInt(asset.amount)
        })
    }

    return userAssets
}

export default getUserAssets;