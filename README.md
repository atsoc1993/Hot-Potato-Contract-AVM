## The Algo Hot Potato Contract

The AlgoPotato contract is a decentralized game using a verifiable random function where two players participate in a game of "Hot Potato" with an equivalent amount of Algorand Standard Assets or Algo— where the winner receives the full amount and the loser receives nothing.

The contract manages game creation, player deposits, VRF-based randomness, and simulates "Hot Potato" back-and-forth transfers before determining a winner.

## Game Rules:

![image](https://github.com/user-attachments/assets/a425709e-d472-472d-9ba9-b29d86686efe)

- Players deposit an asset (Algo or ASA) to start a game.
- A box is created with player details and asset info.
- The second player joins by depositing the same asset amount.
- A VRF Round is selected 9 rounds into the future
- If no second player joins, the first player can cancel and get their deposit back.
- If the VRF round has exceeded 1,512 rounds since its designation, a VRF round 9 rounds into the future will be reset for the box
- If either player opts out of an ASA that prevents the VRF from starting the game, the reward is dispensed to the player who is still opted in
- If both players are opted out, the game remains "live" until one of the player opts in to receive the reward or both opt in to start the game

## Randomness & VRF Integration:

- The Randomness Beacon (VRF) determines the number of "passes" in the game.
- The output is converted into a uint256, and then to a uint64 after the modulo is taken with the integer 240
- The number 240 was selected as the max amount of inner transactions is 256, and we require at least 14 opup budget calls, 1 VRF call,
and a payment/axfer for dispensing the reward to the winner

## Transaction Example Reference

A visual of the full transaction with inner transactions can be seen at the top of this read me in a snippet, or directly on Algokit Lora via the link:
https://lora.algokit.io/testnet/transaction/PJ2TZBXTF5ULU4GASYC3GFZ4RSWA5ILKZNNWG7AJ4YMRLFJEZIAQ









