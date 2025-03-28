import './App.css'
import { useState, useEffect } from 'react'
import fetchGames from './fetchGames'
import { useWallet } from '@txnlab/use-wallet-react'
import createGame from './CreateGame'
import getUserAssets from './GetUserAssets'

function App(){

  const [games, setGames] = useState([])
  const [showWallets, setShowWallets] = useState(false)
  const [userAssets, setUserAssets] = useState([])
  const [selectedAsset, setSelectedAsset] = useState("")
  const [selectedAssetQuantity, setSelectedAssetQuantity] = useState("");
  const providers = useWallet();
  const { wallets, activeWallet, activeAccount, transactionSigner } = useWallet();


  const handleConnect = async (wallet) => {
    try {
      await wallet.connect()
    } catch (error) {
      console.error('Failed to connect:', error)
    } finally {
    }
  }


  useEffect(() => {

    const fetchAndSetGames = async () => {
      const games = await fetchGames()
      setGames(games)
    }

    const fetchUserAssets = async () => {
      const userAssets = await getUserAssets(activeAccount.address)
      setUserAssets(userAssets)
    }

    fetchAndSetGames();

    const interval = setInterval(() => {
      fetchAndSetGames();
      if (activeAccount) {  
        fetchUserAssets();
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className='title'>
      <h1>AlgoPotato</h1>
      <button className='connectButton' onClick={() => setShowWallets(true)}>Connect Wallet</button>
      {showWallets && (
        <div className="modal">
          <div className="modalContent">
            <h3>Select Wallet</h3>
            {providers.wallets.map((provider) => (
              <button key={provider.metadata.id} className="wallet-button" onClick={() => handleConnect(provider)}>
                <img src={provider.metadata.icon} alt={provider.metadata.name} />
                <span>{provider.metadata.name}</span>
              </button>
            ))}
            <button onClick={() => setShowWallets(false)}>Close</button>
          </div>
        </div>
      )}
      <select
        value={selectedAsset}
        onChange={(e) => setSelectedAsset(e.target.value)}
      >
        <option value="" disabled>
          Select an asset
        </option>
        {userAssets.map((asset) => (
          <option key={asset.assetId} value={asset.assetId}>
            {asset.assetId}
          </option>
        ))}
      </select>
      {selectedAsset && (
          <input
            type="number"
            value={selectedAssetQuantity}
            onChange={(e) => setSelectedAssetQuantity(e.target.value)}
            placeholder="Enter quantity"
            min="1"
          />
        )}
      <button 
        onClick={async () => createGame({
          address: activeAccount.address,
          signer: transactionSigner,
          asset: BigInt(selectedAsset),
          amount: BigInt(selectedAssetQuantity)
        })
        }
        disabled={!selectedAsset || !selectedAssetQuantity}
      >
        Create Game
      </button>
      <div className='grid'>
        {games.map((game) => (
        <div className='card' key={game.counter}>
          <p>Player 1:{game.player_one.slice(0, 6)}...</p>
          <p>Player 2: {game.player_two}</p>
          <p>Asset: {game.asset_name}</p>
          <p>Asset ID: {game.asset}</p>
          <p>Amount: {game.asset_amount_text}</p>
          <button>Join Game</button>
        </div>
        ))}

      </div>
    </div>

  )
}

export default App