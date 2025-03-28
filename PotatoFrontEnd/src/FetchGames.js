import { AlgorandClient } from "@algorandfoundation/algokit-utils"
import { ABIType } from "algosdk"

const fetchGames = async () => {
    const algorand = AlgorandClient.testNet()
    const appId = BigInt(import.meta.env.VITE_APP_ID)
    const games = await algorand.app.getBoxNames(appId)
    const potatoBoxNameCoder = ABIType.from('(address,uint64)')
    const potatoBoxValueCoder = ABIType.from('(address,address,uint64,uint64,uint64,uint64,uint64)')
    const zeroAddress = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ'

    const boxInfo = []
    for (const game of games) {
        const boxName = game.nameRaw
        const [address, counter] = potatoBoxNameCoder.decode(boxName)
        const [playerOne, playerOneRound, playerTwo, playerTwoRound, vrfRound, asset, assetAmount] = await algorand.app.getBoxValueFromABIType({
            appId: appId, 
            boxName: boxName, 
            type: potatoBoxValueCoder
        })
        
        let assetAmountText = null
        let assetName = 'Algo'

        if (asset === BigInt(0)) {
            assetAmountText = (Number(assetAmount) / 1_000_000).toLocaleString()
        } else {
            const assetInfo = (await algorand.client.algod.getAssetByID(asset).do()).params
            assetName = assetInfo.name
            assetAmountText = Number(assetAmount) / 10**assetInfo.decimals
        }

        boxInfo.push({
            'counter': counter,
            'creator': address, 
            'player_one': playerOne, 
            'player_one_round': playerOneRound,
            'player_two': playerTwo === zeroAddress ? playerTwo: "None",
            'player_two_round': playerTwoRound,
            'vrf_round': vrfRound,
            'asset': asset,
            'asset_name': assetName,
            'asset_amount': assetAmount,
            'asset_amount_text': assetAmountText
        })
    }

    return boxInfo
}

export default fetchGames