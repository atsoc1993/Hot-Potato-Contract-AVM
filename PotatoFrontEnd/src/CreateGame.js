import { AlgorandClient } from "@algorandfoundation/algokit-utils";
import { AlgoPotatoClient } from "./AlgoPotatoClient";
import { Config } from '@algorandfoundation/algokit-utils'

Config.configure({
  debug: true,
})

const createGame = async ({ address, signer, asset, amount }) => {

    const algorand = AlgorandClient.testNet()
    const appId = BigInt(import.meta.env.VITE_APP_ID)
    
    const algoPotatoClient = algorand.client.getTypedAppClientById(AlgoPotatoClient, {
        appId: appId,
        defaultSender: address,
        defaultSigner: signer,
    })

    const appAddress = algoPotatoClient.appAddress


    const contractAssets = (await algorand.client.algod.accountInformation(appAddress).do()).assets
    const contractOptedIntoAsset = contractAssets.some(
        contractAsset => contractAsset.assetId === asset
    )


    const group = algoPotatoClient.newGroup()

    if (!contractOptedIntoAsset && asset !== BigInt(0)) {
        const optinFeeTx = algorand.createTransaction.payment({
            amount: (100_000).microAlgo(),
            sender: address,
            receiver: appAddress,

        })

        group.assetOptIn({
            args: {
                asset: asset,
                mbrPayment: optinFeeTx
            },
            maxFee: (10_000).microAlgo()
        })
    }


    let assetTransfer = null

    if (asset === BigInt(0)) {
        assetTransfer = await algorand.createTransaction.payment({
            sender: address,
            receiver: appAddress,
            amount: amount,
        })

    } else {

        console.log(address)
        assetTransfer = await algorand.createTransaction.assetTransfer({
            amount: amount,
            assetId: asset,
            sender: address,
            receiver: appAddress,
        })
    }    const mbrFee = await algorand.createTransaction.payment({
        sender: address,
        receiver: appAddress,
        amount: (60_100).microAlgo(), 

    })


    group.createGame({
        args: {
            assetDeposit: assetTransfer,
            mbrFee: mbrFee,
        },
        maxFee: (10_000).microAlgo()
    })

    
    try {
        const response = await group.send({
            coverAppCallInnerTransactionFees: true
            
        })

        console.log("Transaction response:", response)
        return response
    } catch (error) {
        console.error("Error during transaction:", error)
        throw error
    }
}

export default createGame