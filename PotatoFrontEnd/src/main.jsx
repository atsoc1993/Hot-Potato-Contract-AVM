import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import { WalletManager, WalletProvider, NetworkId, WalletId } from '@txnlab/use-wallet-react'
import { Buffer } from 'buffer'


window.Buffer = Buffer
window.global = window

const manager = new WalletManager({
  defaultNetwork:NetworkId.TESTNET,
  wallets: [WalletId.PERA, WalletId.DEFLY] //WalletId.EXODUS, WalletId.LUTE] Exodus not available default error, similar issue with Lute
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <WalletProvider manager={manager}>
    <App />
    </WalletProvider>
  </StrictMode>,
)
