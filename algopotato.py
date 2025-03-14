from algopy import ARC4Contract, BoxMap, UInt64, arc4, gtxn, TransactionType, Global, subroutine, Txn, Application, urange, Bytes, op, itxn, String, ensure_budget, OpUpFeeSource, Asset
from algopy.arc4 import abimethod, Struct, Address, abi_call, UInt256


'''The box name structure for a game'''
class GameBoxName(Struct):
    player_1: Address
    counter: arc4.UInt64


'''The box value structure for a game'''
class GameBoxValue(Struct):
    player_1: Address
    player_2: Address
    player_1_round: arc4.UInt64
    player_2_round: arc4.UInt64
    vrf_round: arc4.UInt64
    asset: arc4.UInt64
    asset_amount: arc4.UInt64


'''The full contract below'''
class AlgoPotato(ARC4Contract):

    def __init__(self) -> None:
    
        '''Initialize global states for:
            - Total # of Games played (excludes cancelled games or forfeits if one of the players opts out of an asset, preventing the game from proceeding)
            - A unique counter, used in the box name structure for a game so that no duplicate box names are possible
            - Defining the BoxMap for the Game Box Name and Value, no key prefix is used
            - The Randomness Beacon (VRF) App ID (testnet), mainnet is commented out
        '''
        self.games_played = UInt64(0)
        self.counter = UInt64(0)
        self.game_box = BoxMap(GameBoxName, GameBoxValue, key_prefix='')
        self.vrf_app_id = Application(600011887) #Testnet
       # self.vrf_app_id = Application(1615566206) Mainnet


    @subroutine
    def contract_is_receiver(
        self,
        txn: gtxn.Transaction,
    ) -> None:
        '''
        Whether the transaction is a payment or asset transfer, verify that the current contract is the receiver via subroutine
        '''
        if txn.type == TransactionType.Payment:
            assert txn.receiver == Global.current_application_address
        elif txn.type == TransactionType.AssetTransfer:
            assert txn.asset_receiver == Global.current_application_address

    @abimethod
    def asset_opt_in(
        self,
        asset: Asset,
        mbr_payment: gtxn.Transaction
    ) -> None:
        
        '''
        Confirm the minimum balance requirement for the asset opt in of 100,000 Microalgo, or 0.1 Algo, was sent to the contract
        (Prevents potential usage of Algo funds reserves for games or excess mbr from box deletions)
        '''
        self.contract_is_receiver(mbr_payment)

        if Global.current_application_address.is_opted_in(asset) == False:
            assert mbr_payment.amount == 100_000
            self.opt_into_asset(asset)

        else:
            assert mbr_payment.amount == 0


    @subroutine
    def opt_into_asset(
        self,
        asset: Asset,
    ) -> None:
        '''
        Actually opt into an asset via subroutine
        '''
        itxn.AssetTransfer(
            xfer_asset=asset,
            asset_receiver=Global.current_application_address
        ).submit()


    @subroutine
    def get_asset_deposit_details(
        self,
        asset_deposit: gtxn.Transaction,
    ) -> tuple[UInt64, UInt64]:

        '''
        Obtains and returns the asset ID (0 if Algo) and amount transferred for game initialization only
        Asserts that the asset deposit is either a Payment or Asset Transfer Transactions
        '''
        asset_id = UInt64(0)
        amount_deposited = UInt64(0)

        assert asset_deposit.type in (TransactionType.Payment, TransactionType.AssetTransfer)

        if asset_deposit.type == TransactionType.Payment:
            asset_id = UInt64(0)
            amount_deposited = asset_deposit.amount

        elif asset_deposit.type == TransactionType.AssetTransfer:
            asset_id = asset_deposit.xfer_asset.id
            amount_deposited = asset_deposit.asset_amount

        assert amount_deposited != 0

        return asset_id, amount_deposited

        
    @subroutine
    def get_game_box_name(
        self
    ) -> GameBoxName:
        '''
        Constructs a GameBoxName instance when creating a game using the sender's address and the current global counter
        '''
        user_addr = Address(Txn.sender)
        counter = arc4.UInt64(self.counter)

        return GameBoxName(
            player_1=user_addr,
            counter=counter
        )
    
    @subroutine
    def get_game_box_value(
        self,
        asset_id: UInt64,
        asset_amount: UInt64
    ) -> GameBoxValue:
        '''
        Constructs a GameBoxValue instance template when creating a game,
        Player 1 address and round field is set to the sender and current round
        Player 2 address is placeholded with the zero address, player round with 0, and vrf round with 0 until another player joins the game
        '''
        user_addr = Address(Txn.sender)

        return GameBoxValue(
                player_1=user_addr,
                player_2=Address(Global.zero_address),
                player_1_round=arc4.UInt64(Global.round),
                player_2_round=arc4.UInt64(0),
                vrf_round=arc4.UInt64(0),
                asset=arc4.UInt64(asset_id),
                asset_amount=arc4.UInt64(asset_amount)
        )
    
    @subroutine
    def verify_mbr_paid(
        self,
        mbr_fee: gtxn.Transaction
    ) -> None:
        '''
        This method verifies the minimum balance requirement is paid for box creation for game details when creating a game
        2500 Microalgo for a new box, then the total number of bytes needed for the key and value collectively multiplied by 400 microalgo
        The BoxName comprises of an address and uint64, requiring 32 + 8 bytes
        The BoxValue comprises of a struct, with 2 address' (64 bytes), and 5 uint64's (40 bytes).
        Total Bytes = 144
        (Note that we do not use any dynamic arrays so 2 prefix bytes do not need to be taken into account)
        '''
    
        assert mbr_fee.amount == UInt64(2500) + (144 * 400)

    @abimethod
    def create_game(
        self,
        asset_deposit: gtxn.Transaction,
        mbr_fee: gtxn.Transaction
    ) -> None:
        '''
        Initializes a game
        - Dynamically confirms the contract is the receiver of both the asset deposit and mbr fee
        - Gets the asset id and amount transferred from the asset deposit
        - Constructs a box name instance using the sender and current global counter
        - Constructs a box value template with only non-default values being player 1 address, asset (0 if algo), asset deposit amount, and player 1 round (current round)
        - Writes the box name and value
        '''
        self.contract_is_receiver(asset_deposit)
        self.contract_is_receiver(mbr_fee)

        asset_id, asset_amount = self.get_asset_deposit_details(asset_deposit)

        game_box_name = self.get_game_box_name()

        game_box_value = self.get_game_box_value(asset_id, asset_amount)

        self.game_box[game_box_name] = game_box_value.copy()


    @subroutine
    def verify_player_2_asset_deposit(
        self,
        asset_deposit: gtxn.Transaction,
        game_box_value: GameBoxValue
    ) -> None:
        '''
        Asserts the asset deposit is an asset transfer or payment
        Asserts the asset deposited matches the games details
        eg; if player 1 deposited 10 Algo, player 2 must deposit 10 Algo
        '''
        
        assert asset_deposit.type in (TransactionType.AssetTransfer, TransactionType.Payment)

        if asset_deposit.type == TransactionType.Payment:
            assert game_box_value.asset == 0
            assert game_box_value.asset_amount == asset_deposit.amount

        else:
            assert game_box_value.asset == asset_deposit.xfer_asset.id
            assert game_box_value.asset_amount == asset_deposit.asset_amount
        
    @subroutine
    def update_game_box_details(
        self,
        game_box: GameBoxValue
    ) -> GameBoxValue:
        '''
        Updates the current game box with player 2's information
        Asserts player 2 is currently the zero address, as that is default value for a game that has no player 2 yet,
        Sets player 2 address, the current round player 2 registered to the game, and a VRF round 9 rounds into the future
        Returns the updated game box
        '''

        assert game_box.player_2 == Global.zero_address
        game_box.player_2 = Address(Txn.sender)
        game_box.player_2_round = arc4.UInt64(Global.round)
        game_box.vrf_round = arc4.UInt64(Global.round + 9)

        return game_box

    @abimethod
    def prime_game_vrf(
        self,
        game_box_name: GameBoxName,
        asset_deposit: gtxn.Transaction,
    ) -> None:
        
        '''
        Asserts the contract is the receiver of player 2's asset deposit
        Gets the current game details
        Verifies that the asset deposit matches the game details,
        Updates the current game box with player 2's information
        Writes the updated information into box storage
        '''
        self.contract_is_receiver(asset_deposit)

        game_box = self.game_box[game_box_name].copy()

        self.verify_player_2_asset_deposit(asset_deposit, game_box)

        game_box = self.update_game_box_details(game_box)
        self.game_box[game_box_name] = game_box.copy()


    @subroutine
    def get_vrf_output_modulo(
        self,
        game_box: GameBoxValue
    ) -> tuple[UInt64, bool]:
        
        '''
        Inputs the GameBoxValue as bytes as an argument to the 'must_get' method of the VRF contract
        'must_get' differs from 'get' in that it fails if the VRF round is not ready to be processed yet
        If the VRF round has exceeded 1,512 rounds since its designation, a VRF round 9 rounds into the future will be set for the box
        The output is converted into a uint256, and then to a uint64 after the modulo is taken with the integer 240
        The number 240 was selected as the max amount of inner transactions is 256, and we require at least 14 opup budget calls, 1 VRF call,
        and a payment/axfer for dispensing the reward to the winner
        
           '''
        vrf_round = game_box.vrf_round

        if Global.round - vrf_round.native > 1512:
            return UInt64(0), False

        game_box_as_bytes = game_box.bytes

        result, txn = abi_call[Bytes](
            'must_get(uint64,byte[])byte[]',
            vrf_round,
            game_box_as_bytes,
            app_id=600011887,
        )

        vrf_bytes_as_integer = UInt256.from_bytes(result)
        modulo_240_vrf_bytes_as_int = op.btoi((vrf_bytes_as_integer.native % 240).bytes)

        return modulo_240_vrf_bytes_as_int, True
    
    @subroutine
    def process_hot_potato(
        self,
        game_box: GameBoxValue,
        modulo_240_vrf_bytes_as_int: UInt64,
    ) -> Address:
        '''
        The contract transfers 0 Algo or 0 of the Asset to player 1 and player 2 until the target modulo result is reached,
        This provides a sort of "Hot Potato" effect, where the last 'Hot Potato' dispenses the reward to the winner
        '''
        player_1 = game_box.player_1.native
        player_2 = game_box.player_2.native
        
        asset_id = game_box.asset.native
        asset_amount = game_box.asset_amount.native * 2

        potato_holder = Global.zero_address

        for i in urange(modulo_240_vrf_bytes_as_int + 1):
            if i % 2 == 0:
                potato_holder = player_1

            if i % 2 != 0:
                potato_holder = player_2

            if i == modulo_240_vrf_bytes_as_int:
                if asset_id == 0:
                    itxn.Payment(
                        receiver=potato_holder,
                        amount=asset_amount,
                    ).submit()
                else:
                    itxn.AssetTransfer(
                        xfer_asset=asset_id,
                        asset_receiver=potato_holder,
                        asset_amount=asset_amount,
                    ).submit()
                break

            if asset_id == 0:
                itxn.Payment(
                    receiver=potato_holder,
                    amount=0,
                ).submit()
            else:
                itxn.AssetTransfer(
                    xfer_asset=asset_id,
                    asset_receiver=potato_holder,
                    asset_amount=0,
                ).submit()

        return Address(potato_holder)

    @subroutine
    def verify_both_users_opted_in(
        self,
        game_box: GameBoxValue
    ) -> tuple[bool, String]:
        '''
        Verifies both users are opted in or if the asset is Algorand that does not require being opted into, returns an empty string if True 
        The first user to be detected to be currently opted out (starting with Player 1)
        forfeits the reward, and it is dispensed to the other player,
        if both users have opted out, this will fail, and the first user to opt back in can redeem the full reward
        '''
        player_1 = game_box.player_1.native
        player_2 = game_box.player_2.native

        asset = game_box.asset.native
        asset_amount = game_box.asset_amount.native * 2

        if asset == 0:
            return True, String('')
        
        elif player_1.is_opted_in(Asset(asset)) == False:
            itxn.AssetTransfer(
                xfer_asset=asset,
                asset_receiver=player_2,
                asset_amount=asset_amount
            ).submit()

            return False, String("Player 1 Forfeit by opting out")
        
        elif player_2.is_opted_in(Asset(asset)) == False:
            itxn.AssetTransfer(
                xfer_asset=asset,
                asset_receiver=player_1,
                asset_amount=asset_amount
            ).submit()

            return False, String("Player 2 Forfeit by opting out")

        else:
            return True, String('')
        
    @subroutine
    def game_is_ready(
        self,
        game_box: GameBoxValue
    ) -> None:
        '''Assert that the VRF round in the game has been set, if not then there is no player 2 as of yet'''
        assert game_box.vrf_round != 0
    
    @abimethod
    def play_game(
        self,
        game_box_name: GameBoxName,
    ) -> String:
        '''Initializes the "Hot Potato" Game
            - Starts with an ensure budget requiring 14 inner txns
            - Gets the game information
            - Ensures a player 2 has joined and the game is ready
            - Gets the VRF Output % 240, see "get_vrf_output_modulo" for information on why the # 240 was chosen
            - Verifies both users are opted in or asset is Algorand which does not require opt in
            - If either of the users are not opted into the asset then the reward goes to the user that is still opted in
            - If both users are not opted in the first to opt in can claim the reward
            - If the VRF round has expired (1,512 rounds have passed since the VRF round selected) a new VRF round is created 9 rounds into the future
            - Hot Potato game starts, the contract sends Algo or Asset zero amount transactions to both players until the target modulo is reached
            - The player the 'Hot Potato' was on at the target modulo receives the reward
            - The reward is dispensed and the box is deleted to prevent state bloat
            - A little string is returned that states which player won
            '''
        ensure_budget(
            required_budget=10_000, 
            fee_source=OpUpFeeSource.GroupCredit
        )

        game_box = self.game_box[game_box_name].copy()

        self.game_is_ready(game_box)

        modulo_240_vrf_bytes_as_int, valid_vrf_round = self.get_vrf_output_modulo(game_box.copy())

        both_users_opted_into_asset, return_message = self.verify_both_users_opted_in(game_box.copy())

        if valid_vrf_round == False:
            game_box.vrf_round = arc4.UInt64(Global.round + 9)
            self.game_box[game_box_name] = game_box.copy()
            return String("VRF Round expired")
        
        elif not both_users_opted_into_asset:

            del self.game_box[game_box_name]

            self.games_played += 1

            return return_message

        else:
            potato_holder = self.process_hot_potato(game_box, modulo_240_vrf_bytes_as_int)

            player_1 = game_box.player_1

            del self.game_box[game_box_name]

            self.games_played += 1

            if potato_holder == player_1:
                return String("Player 1 Wins!")
            else:
                return String("Player 2 Wins!")
            

        
    @abimethod
    def cancel_game(
        self,
        game_box_name: GameBoxName
    ) -> None:
        '''
        Cancels a game if and only if there is no active player 2
        Dispenses the asset deposit to player 1
        '''
        game_box = self.game_box[game_box_name].copy()

        player_1 = game_box.player_1.native
        player_2 = game_box.player_2.native


        asset = game_box.asset.native
        asset_amount = game_box.asset_amount.native

        assert player_2 == Global.zero_address

        if asset == 0:
            itxn.Payment(
                receiver=player_1,
                amount=asset_amount
            ).submit()

        else:
            itxn.AssetTransfer(
                asset_receiver=player_1,
                xfer_asset=asset,
                asset_amount=asset_amount
            ).submit()

        del self.game_box[game_box_name]