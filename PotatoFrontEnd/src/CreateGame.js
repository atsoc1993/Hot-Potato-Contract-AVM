import { AlgorandClient } from "@algorandfoundation/algokit-utils";
import { AlgoPotatoClient } from "./AlgoPotatoClient";


const createGame = async ({ address, signer, asset, amount }) => {

    const algorand = AlgorandClient.testNet()
    const appId = BigInt(import.meta.env.VITE_APP_ID)
    
    const algoPotatoClient = algorand.client.getTypedAppClientById(AlgoPotatoClient, {
        appId: appId,
        defaultSender: address,
        defaultSigner: signer,
    })

    const appAddress = algoPotatoClient.appAddress

    let assetTransfer = null

    if (asset === BigInt(0)) {
        assetTransfer = algorand.createTransaction.payment({
            sender: address,
            receiver: appAddress,
            amount: amount,
        })

    } else {

        assetTransfer = algorand.createTransaction.assetTransfer({
            amount: amount,
            assetId: asset,
            sender: address,
            receiver: appAddress,
        })
    }

    const mbrFee = algorand.createTransaction.payment({
        sender: address,
        receiver: appAddress,
        amount: (60_100).microAlgo(), 
    })

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

    group.createGame({
        args: {
            assetDeposit: assetTransfer,
            mbrFee: mbrFee,
        },
        maxFee: (10_000).microAlgo()
    })

    const composer = await group.composer();
    const builtGroup = await composer.build();
    const txs = builtGroup.transactions;
    console.log(txs);
    
    try {
        const response = await group.send({
            
            coverAppCallInnerTransactionFees: true,
            populateAppCallResources: true,
        })
        console.log("Transaction response:", response)
        return response
    } catch (error) {
        console.error("Error during transaction:", error)
        throw error
    }
}

export default createGame