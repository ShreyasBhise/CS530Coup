import Card
import Agent
import random

challengable_actions = set(['Assassinate', 'Tax', 'Steal', 'Exchange'])
blockable_actions = (['Assassinate', 'Steal', 'Foreign Aid'])

class Game:
    # Move state is defined as follows:
    # 0 = current_player needs to make selection
    # 1 = selection made, nothing else
    # 2 = selection made, challenge
    # 3 = pick card for ^
    # 4 = selection made, post-challenge
    # 5 = selection made, block
    # 6 = selection made, block, challenge
    # 7 = pick card for ^
    # 7 = selection made, post-block
    # 8 = execute move
    # 9 = end turn phase
    def __init__(self, num_players):
        self.num_players = num_players
        self.deck = Card.Deck()
        self.player_list = list()
        for i in range(num_players):
            self.player_list.append(Agent.RandomAgent(i))
            for _ in range(2):
                self.player_list[i].cards.append(self.deck.deal())
        self.current_player = random.randint(0, num_players - 1)
        self.move_state = 0
        self.action = ""
        self.target = 0
        self.blocker = 0
        self.win_challenge = False
        self.challenger = None
        self.winner = -1
    
    def run_game(self):
        while self.winner == -1:
            self.step()
        return self.winner

    def step(self):
        if(self.move_state == 0):
            (self.action, self.target) = self.player_list[self.current_player].take_action(self)
            self.move_state = 1
            return
        elif (self.move_state == 1):
            self.move_state = 4
            if self.action in challengable_actions:
                for player in self.player_list:
                    if player.is_alive() and player.id != self.current_player and player.challenge(self):
                        self.challenger = player
                        self.move_state = 2
                        break
            return
        elif (self.move_state == 2):
            self.win_challenge = resolve_normal_challenge(self, self.player_list[self.current_player], self.challenger, self.action)
            self.move_state = 3
            return
        elif (self.move_state == 3):
            if (self.win_challenge==True): # challenger must reveal a card
                self.challenger.flip_card(self)
                self.move_state = 4
                return
            else: # player must reveal a card
                self.player_list[self.current_player].flip_card(self)
                self.move_state = 9
                return
        elif (self.move_state == 4):
            if self.action in blockable_actions:
                self.move_state = 8
                #Any player can block foreign aid
                if self.action == 'Foreign Aid':
                    for player in self.player_list:
                        if player.is_alive() and player.id != self.current_player and player.block(self):
                            self.blocker = player.id
                            self.move_state=5
                            break

                #Blocking assassination/stealing can only be done by the target
                else:
                    if self.player_list[self.target].is_alive() and self.player_list[self.target].block(self):
                        self.blocker = self.target
                        self.move_state=5
                return
            else:
                self.move_state = 8
                return
        elif (self.move_state == 5):
            print(str(self.blocker) + ' is blocking ' + self.action + ' from ' + str(self.current_player))
            self.move_state = 9
            for player in self.player_list:
                if player.id == self.blocker:
                    continue
                if player.is_alive() and player.challenge(self):
                    self.challenger = player
                    self.move_state = 6
                    break
            return
        elif (self.move_state == 6):
            self.win_challenge = resolve_block_challenge(self, self.player_list[self.blocker], self.challenger, self.action)
            self.move_state = 7
            return
        elif (self.move_state == 7):
            if (self.win_challenge==True): # challenger must reveal a card
                self.challenger.flip_card(self)
                self.move_state = 9 # move doesn't get executed
                return
            else: # blocker must reveal a card
                self.player_list[self.blocker].flip_card(self)
                self.move_state = 8 # move does get executed
                return
        elif (self.move_state == 8): # move goes through sucessfully
            if self.action == 'Income':
                self.player_list[self.current_player].coins += 1
            elif self.action == 'Foreign Aid':
                self.player_list[self.current_player].coins += 2
            elif self.action == 'Tax':
                self.player_list[self.current_player].coins += 3
            elif self.action == 'Coup':
                self.player_list[self.current_player].coins -= 7
                self.player_list[self.target].flip_card(self)
            elif self.action == 'Assassinate':
                self.player_list[self.current_player].coins -= 3
                if self.player_list[self.target].is_alive():
                    self.player_list[self.target].flip_card(self)
            elif self.action == 'Exchange':
                exchangable = [self.deck.deal(), self.deck.deal()]
                returned_cards = self.player_list[self.current_player].exchange(self, exchangable)
                self.deck.return_cards(returned_cards)
            elif self.action == 'Steal':
                steal = min(self.player_list[self.target].coins, 2)
                self.player_list[self.target].coins -= steal
                self.player_list[self.current_player].coins += steal
            self.move_state = 9
            return
        elif (self.move_state == 9): # turn has ended
            self.move_state = 0
            alive_players = 0
            for player in self.player_list:
                if(player.is_alive()):
                    alive_players += 1 
            self.current_player = (self.current_player + 1) % self.num_players
            while not self.player_list[self.current_player].is_alive():
                self.current_player = (self.current_player + 1) % self.num_players
            if not alive_players>1:
                for player in self.player_list:
                    if(player.is_alive()):
                        self.winner = player.id
                if self.winner == -1:
                    print("error: no winner")
                    self.winner = -2
            return


# returns true if player has card, false if player doesn't have card
def resolve_normal_challenge(game:Game, actor:Agent, challenger:Agent, action:str) -> bool:
    print(str(challenger.id) + ' is challenging ' + str(actor.id) + ' on ' + action)
    index = -1
    possible_moves = []
    for i in range(2):
        if not actor.cards[i].is_revealed:
            if action == actor.cards[i].valid_actions:
                index = i
    #Actor must reveal a card
    if index == -1:
        #actor.flip_card()
        print(str(actor.id) + " failed challenge.")
        return False
    #Challenger must reveal a card, player gets a new card    
    else:
        #challenger.flip_card()
        print(str(challenger.id) + ' failed challenge.')
        ans = list()
        ans.append(actor.cards.pop(index))
        game.deck.return_cards(ans)
        actor.cards.append(game.deck.deal())
        return True

# returns true if blocker has card, false if blocker doesn't have card
def resolve_block_challenge(game:Game, blocker:Agent, challenger:Agent, action:str) -> bool:
    print(str(challenger.id) + ' is challenging ' + str(blocker.id) + ' on ' + action)
    index = -1
    possible_moves = []
    for i in range(2):
        if not blocker.cards[i].is_revealed:
            if action == blocker.cards[i].can_block:
                index = i
    #Blocker must reveal a card
    if index == -1:
        #actor.flip_card()
        print(str(blocker.id) + " failed challenge.")
        return False
    #Challenger must reveal a card, blocker gets a new card    
    else:
        #challenger.flip_card()
        print(str(challenger.id) + ' failed challenge.')
        ans = list()
        ans.append(blocker.cards.pop(index))
        game.deck.return_cards(ans)
        blocker.cards.append(game.deck.deal())
        return True

# def resolve_challenge(actor:Agent, challenger:Agent, action:str, is_block:bool, deck:Card.Deck) -> bool:
#     print(str(challenger.id) + ' is challenging ' + str(actor.id) + ' on ' + action)
#     index = -1
#     possible_moves = []
#     for i in range(2):
#         if not actor.cards[i].is_revealed:
#             if is_block and action == actor.cards[i].can_block:
#                 index = i
#             else:
#                 if action == actor.cards[i].valid_actions:
#                     index = i
            
#     #Actor must reveal a card
#     if index == -1:
#         actor.flip_card()
#         print(str(actor.id) + " failed challenge.")
#         return False
#     #Challenger must reveal a card, player gets a new card    
#     else:
#         challenger.flip_card()
#         print(str(challenger.id) + ' failed challenge.')
#         ans = list()
#         ans.append(actor.cards.pop(index))
#         deck.return_cards(ans)
#         actor.cards.append(deck.deal())
#         return True

# def resolve_block(actor:Agent, blocker:Agent, action:str, target:int, deck:Card.Deck) -> bool: 
#     print(str(blocker.id) + ' is blocking ' + action + ' from ' + str(actor.id))
#     for player in player_list:
#         if player.id == blocker.id:
#             continue
#         if player.is_alive() and player.challenge((action, target), player_list):
#             return not resolve_challenge(blocker, player, action, True, deck)

#     return True

    
#Target is alive, action can be taken on them
def execute_move(actor:Agent, action:str, target:int, deck:Card.Deck):
    print(f'{actor.id} is trying to {action} player {target}.')

    win_challenge = None
    #Check for challenge
    if action in challengable_actions:
        for player in player_list:
            if player.is_alive() and player.id != actor.id and player.challenge((action, target), player_list):
                win_challenge = resolve_challenge(actor, player, action, False, deck)
                break

    if win_challenge is False:
        return
    #Check for block
    execute_move = True
    if action in blockable_actions:
        #Any player can block foreign aid
        if action == 'Foreign Aid':
            for player in player_list:
                if player.is_alive() and player.id != actor.id and player.block(action, player_list):
                    execute_move = resolve_block(actor, player, action, target, deck)
                    break

        #Blocking assassination/stealing can only be done by the target
        else:
            if player_list[target].is_alive() and player_list[target].block((action, target), player_list):
                execute_move = resolve_block(actor, player_list[target], action, target, deck)

    if execute_move:
        return
    #Execute the move
    if action == 'Income':
        actor.coins += 1
    elif action == 'Foreign Aid':
        actor.coins += 2
    elif action == 'Tax':
        actor.coins += 3
    elif action == 'Coup':
        actor.coins -= 7
        player_list[target].flip_card()
    elif action == 'Assassinate':
        actor.coins -= 3
        if player_list[target].is_alive():
            player_list[target].flip_card()
    elif action == 'Exchange':
        exchangable = [deck.deal(), deck.deal()]
        returned_cards = actor.exchange(exchangable)
        deck.return_cards(returned_cards)
    elif action == 'Steal':
        steal = min(player_list[target].coins, 2)
        player_list[target].coins -= steal
        actor.coins += steal

def run_game(num_players:int, player_list:list, deck:Card.Deck):
    continue_game = True
    current_player = random.randint(0, num_players - 1)
    while continue_game:
        (action, target) = player_list[current_player].take_action(player_list)
        execute_move(player_list[current_player], action, target, deck)
        for player in player_list:
            print(f'{player.id} has {player.lives} lives left')
        alive_players = 0

        for player in player_list:
            if(player.is_alive()):
                alive_players += 1
                
        current_player = (current_player + 1) % num_players
        while not player_list[current_player].is_alive():
            current_player = (current_player + 1) % num_players
            
        continue_game = True if alive_players > 1 else False
        
    for player in player_list:
        if player.is_alive():
            print(player.id, end=' ')
            print()

if __name__ == '__main__':
    num_players = 6
    game = Game(num_players)

    for i in range(num_players):
        print(i)
        print(game.player_list[i].cards[0])
        print(game.player_list[i].cards[1])
        print('---------------------------')

    winner =game.run_game()
    print(winner)