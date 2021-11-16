import Card
import Agent
import random
player_list = list()


def resolve_challenge(actor:Agent, challenger:Agent, action:str, is_block:bool) -> bool:

    index = -1
    possible_moves = []
    for i in range(2):
        if not actor.cards[i].is_revealed:
            if is_block and action == actor.cards[i].can_block:
                index = i
            else:
                if action == actor.cards[i].valid_actions:
                    index = i
            
    #Actor must reveal a card
    if index == -1:
        actor.flip_card()
        print(str(actor.id) + " failed challenge.")
        return True
    #Challenger must reveal a card, player gets a new card    
    else:
        challenger.flip_card()
        ans = list()
        ans.append(actor.cards.pop(index))
        deck.return_cards(ans)
        player.cards.append(deck.deal())
        return False
def resolve_block(actor:Agent, blocker:Agent, action:str, target:int) -> bool:
    for player in player_list:
        if player.id == blocker.id:
            continue
        if player.is_alive() and player.challenge((action, target), player_list):
            return resolve_challenge(actor, player, action, True)

    
#Target is alive, action can be taken on them
def execute_move(actor:Agent, action:str, target:int):
    print(str(actor.id), end=' ')
    print(action)
    challengable_actions = set(['Assassinate', 'Tax', 'Steal', 'Exchange'])
    blockable_actions = (['Assassinate', 'Steal', 'Foreign Aid'])

    win_challenge = None
    #Check for challenge
    if action in challengable_actions:
        for player in player_list:
            if player.is_alive and player.challenge((action, target), player_list):
                win_challenge = resolve_challenge(actor, player, action, False)
                break

    if win_challenge is False:
        return
    #Check for block
    execute_move = True
    if win_challenge is None and action in blockable_actions:
        #Any player can block foreign aid
        if action == 'Foreign Aid':
            for player in player_list:
                if player.is_alive and player.block(action, player_list):
                    execute_move = resolve_block(actor, player, action, target)
                    break

        #Blocking assassination/stealing can only be done by the target
        else:
            if player_list[target].block((action, target), player_list):
                execute_move = resolve_block(actor, player_list[target], action, target)

    if not execute_move:
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
        player_list[target].flip_card()
    elif action == 'Exchange':
        exchangable = [deck.deal(), deck.deal()]
        returned_cards = actor.exchange(exchangable)
        deck.return_cards(returned_cards)
    elif action == 'Steal':
        steal = min(player_list[target].coins, 2)
        player_list[target].coins -= steal
        actor.coins += steal

if __name__ == '__main__':
    deck = Card.Deck()
    num_players = 3
    
    continue_game = True
    for i in range(num_players):
        player_list.append(Agent.RandomAgent(i))
        for _ in range(2):
            player_list[i].cards.append(deck.deal())

    for i in range(num_players):
        print(i)
        print(player_list[i].cards[0])
        print(player_list[i].cards[1])
        print('---------------------------')

    current_player = random.randint(0, num_players - 1)
    while continue_game:
        (action, target) = player_list[current_player].take_action(player_list)
        execute_move(player_list[current_player], action, target)

        alive_players = 0

        for player in player_list:
            if(player.is_alive()):
                alive_players += 1
        current_player = (current_player + 1) % num_players

        continue_game = True if alive_players > 1 else False


    for player in player_list:
        if player.is_alive():
            print(player.id, end=' ')
            print()