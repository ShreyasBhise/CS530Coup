import Game
import copy

class Agent:
     def __init__(self, id):
          self.lives = 2
          self.id = id
          self.coins = 2
          self.cards = []
          self.valid_moves = {'Income', 'Foreign Aid', 'Coup'}
     
     def get_card(self, card):
          self.cards.append(card)

     def take_action(self, game:Game):
          return

     def challenge(self, game:Game):
          return False

     def block(self, game:Game):
          return False
          
     def flip_card(self, game:Game):
          self.lives -= 1

     def is_alive(self):
          return self.lives > 0

     def exchange(self, game:Game, new_cards:list) -> list:
          return new_cards

     def __repr__(self):
          return str(self.id)

import random
class RandomAgent(Agent):
     #           bank     bank          player   bank    player       player    bank
     moves = ['Income', 'Foreign Aid', 'Coup', 'Tax', 'Assassinate', 'Steal', 'Exchange']
     need_target = set(['Coup', 'Assassinate', 'Steal'])
     def __init__(self, id):
          super().__init__(id)
     
     def take_action(self, game:Game):
          invalid = True
          action = None
          target = self.id
          while invalid:
               if(self.coins >= 10):
                    action = 'Coup'
               else:
                    action = random.choice(self.moves)
                    if (action == 'Coup' and self.coins < 7) or (action == 'Assassinate' and self.coins < 3):
                         continue
                    if action == 'Steal': # picks a new action if 'Steal' and every alive target has 0 coins
                         total_coins = 0
                         for target in range(0, len(game.player_list)):
                              if target == self.id or not game.player_list[target].is_alive():
                                   continue
                              total_coins += game.player_list[target].coins
                         if total_coins == 0:
                              continue

               if action in self.need_target:
                    while target == self.id or not game.player_list[target].is_alive() or (game.player_list[target].coins == 0 and action == 'Steal'):
                         target = random.randint(0, len(game.player_list) - 1)
               invalid = False
          return (action, target)

     def challenge(self, game:Game):
          return random.choice([True,False])

     def block(self, game:Game):
          return random.choice([True,False])
          
     def flip_card(self, game:Game):
          super().flip_card(game)
          if self.cards[0].is_revealed and self.cards[1].is_revealed:
               return
          card = self.cards[random.randint(0, 1)]
          while card.is_revealed:
               x = random.randint(0, 1)
               card = self.cards[x]
          card.life_lost()

     def exchange(self, game:Game, new_cards:list) -> list:
          # print('Player ' + str(self.id) + ' Exchanging Cards: ')
          # for card in self.cards:
          #      print(card)
          # print('For: ')
          # for card in new_cards:
          #      print(card)
          card_list = list()
          card_list += new_cards

          to_pop = -1
          for i in range(len(self.cards)):
               if not self.cards[i].is_revealed:
                    card_list.append(self.cards[i])
                    to_pop = i

          for _ in range(self.lives):
               self.cards.append(card_list.pop(random.randint(0, len(new_cards)-1)))
          
          for i in range(1, -1, -1):
               if not self.cards[i].is_revealed:
                    self.cards.pop(i)
          # print('End: ')
          # for card in self.cards:
          #      print(card)
          return card_list

     def __repr__(self):
          super().__repr__()
          
class MonteCarloTreeAgent(Agent): # currently assumes all knowledge of other players
     #           bank     bank          player   bank    player       player    bank
     moves = ['Income', 'Foreign Aid', 'Coup', 'Tax', 'Assassinate', 'Steal', 'Exchange']
     need_target = set(['Coup', 'Assassinate', 'Steal'])
     def __init__(self, id):
          super().__init__(id)
     
     # Take deep copied game, and alters it to reflect the agents view of the board
     def dup_game(self, test_game:Game):
          replacement = RandomAgent(self.id)
          replacement.lives = self.lives
          replacement.coins = self.coins
          replacement.cards = copy.deepcopy(self.cards)
          test_game.player_list[self.id]=replacement
          #randomize unknown cards as agent has no knowledge
          removed_cards = list()
          for i in range(test_game.num_players):
               if i==self.id:
                    continue
               for j in range(1, -1, -1):
                    if test_game.player_list[i].cards[j].is_revealed == False:
                         removed_cards.append(test_game.player_list[i].cards.pop(j))
          test_game.deck.return_cards(removed_cards)
          for i in range(test_game.num_players):
               while(len(test_game.player_list[i].cards)<2):
                    test_game.player_list[i].cards.append(test_game.deck.deal())


     def take_action(self, game:Game):
          if(self.coins>=10):
               return ('Coup', self.id)
          valid_moves = []
          wins_per_move = []
          for move in self.moves:
               if (move == 'Coup' and self.coins < 7) or (move == 'Assassinate' and self.coins < 3):
                    continue
               if move in self.need_target:
                    for target in range(0, len(game.player_list)):
                         if move == 'Steal' and game.player_list[target].coins == 0:
                              continue
                         if target != self.id and game.player_list[target].is_alive():
                              valid_moves.append((move, target))
               else:
                    valid_moves.append((move, self.id))
          
          # run each selection of valid moves 100 times
          for (move, target) in valid_moves:
               wins = 0
               for i in range(100):
                    test_game = copy.deepcopy(game)
                    self.dup_game(test_game)
                    test_game.action = move
                    test_game.target = target
                    test_game.move_state = 1
                    if test_game.run_game() == self.id:
                         wins = wins+1
               wins_per_move.append(wins)
          (move, target) = valid_moves[0]
          max_wins = wins_per_move[0]
          for i in range(1, len(valid_moves)):
               if wins_per_move[i]>max_wins:
                    max_wins = wins_per_move[i]
                    (move, target) = valid_moves[i]
          return (move, target)

     def challenge(self, game:Game):
          true_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               self.dup_game(test_game)
               test_game.challenger = self.id
               if game.move_state==1:
                    test_game.move_state = 2
               else:
                    test_game.move_state = 6
               if test_game.run_game() == self.id:
                    true_wins = true_wins+1
          false_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               self.dup_game(test_game)
               if game.move_state==1:
                    test_game.move_state = 4
               else:
                    test_game.move_state = 9
               if test_game.run_game() == self.id:
                    false_wins = false_wins+1
          selection = True
          if false_wins>true_wins:
               selection = False
          return selection

     def block(self, game:Game):
          true_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               self.dup_game(test_game)
               test_game.blocker = self.id
               test_game.move_state = 5
               if test_game.run_game() == self.id:
                    true_wins = true_wins+1
          false_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               self.dup_game(test_game)
               test_game.move_state = 8
               if test_game.run_game() == self.id:
                    false_wins = false_wins+1
          selection = True
          if false_wins>true_wins:
               selection = False
          return selection
          
     def flip_card(self, game:Game): # still random
          super().flip_card(game)
          if self.cards[0].is_revealed and self.cards[1].is_revealed:
               return
          if self.cards[0].is_revealed:
               self.cards[1].life_lost()
               return
          elif self.cards[1].is_revealed:
               self.cards[0].life_lost()
               return
          else: # could reveal either card
               zero_wins = 0
               for i in range(100):
                    #print('------------------------' + str(self.lives))
                    test_game = copy.deepcopy(game)
                    self.dup_game(test_game)
                    test_game.player_list[self.id].cards[0].life_lost()

                    if game.move_state==3:
                         if game.win_challenge==True:
                              test_game.move_state = 4
                         else:
                              test_game.move_state = 9
                    elif game.move_state==7:
                         if game.win_challenge==True:
                              test_game.move_state = 9
                         else:
                              test_game.move_state = 8
                    else: # move_state is 8
                         test_game.move_state = 9

                    if test_game.run_game() == self.id:
                         zero_wins = zero_wins+1
               one_wins = 0
               for i in range(100):
                    test_game = copy.deepcopy(game)
                    self.dup_game(test_game)
                    test_game.player_list[self.id].cards[0].life_lost()

                    if game.move_state==3:
                         if game.win_challenge==True:
                              test_game.move_state = 4
                         else:
                              test_game.move_state = 9
                    elif game.move_state==7:
                         if game.win_challenge==True:
                              test_game.move_state = 9
                         else:
                              test_game.move_state = 8
                    else: # move_state is 8
                         test_game.move_state = 9
                    if test_game.run_game() == self.id:
                         one_wins = one_wins+1
               if one_wins>zero_wins:
                    self.cards[1].life_lost()
               else:
                    self.cards[0].life_lost()

     def exchange(self, game:Game, new_cards:list) -> list: # this is still random
          card_list = list()
          card_list += new_cards

          to_pop = -1
          for i in range(len(self.cards)):
               if not self.cards[i].is_revealed:
                    card_list.append(self.cards[i])

          for _ in range(self.lives):
               self.cards.append(card_list.pop(random.randint(0, len(new_cards)-1)))
          
          for i in range(1, -1, -1):
               if not self.cards[i].is_revealed:
                    self.cards.pop(i)

          return card_list

     def __repr__(self):
          super().__repr__()

class LookAheadAgent(Agent): # currently assumes all knowledge of other players
     #           bank     bank          player   bank    player       player    bank
     moves = ['Income', 'Foreign Aid', 'Coup', 'Tax', 'Assassinate', 'Steal', 'Exchange']
     need_target = set(['Coup', 'Assassinate', 'Steal'])

     def __init__(self, id):
          super().__init__(id)

     def lookahead(self, game:Game, utility, permutation, depth:int):
          if depth == 3:
               return (utility, permutation)
          if game.move_state == 1:
               if game.action in game.challengable_actions:
                    #challenge
                    game.move_state = 4
                    sum = (0,0)
                    for player in game.player_list:
                         if player == self.id:
                              continue
                         permutation += 1
                         (temp1, temp2) = self.lookahead(game, utility, permutation, depth)
                         temp_game = copy.deepcopy(game)
                         temp_game.move_state = 2
                         temp_game.challenger = player.id
                         permutation += 1
                         (temp3, temp4) = self.lookahead(temp_game, utility, permutation, depth+1)
                         sum += (temp1+temp3, temp2+temp4)
                    
          elif game.move_state == 2:
               game.win_challenge = game.resolve_normal_challenge(game, game.player_list[game.current_player], game.player_list[game.challenger], game.action)
               game.move_state = 3
               permutation += 1
               return self.lookahead(game, utility, permutation, depth)
          elif game.move_state == 3:
               if (game.win_challenge==True): # challenger must reveal a card
                    game.player_list[game.challenger].flip_card(game)
                    if game.player_list[game.target].lives() == 1:
                         utility += 30
                    elif game.player_list[game.target].lives() == 0:
                         utility += 100
                    game.move_state = 4
               else: # player must reveal a card
                    game.player_list[game.current_player].flip_card(game)
                    if self.lives == 1:
                         utility -= 30
                    elif self.lives == 0:
                         utility -= 100
                    game.move_state = 9
               return self.lookahead(game, utility, permutation, depth)
          elif game.move_state == 4:
               game.move_state = 8

               if game.action in game.blockable_actions:
                    #Any player can block foreign aid
                    if game.action == 'Foreign Aid':
                         for player in game.player_list:
                              if player.is_alive() and player.id != game.current_player and player.block(game):
                                   permutation+=1
                                   game.blocker = player.id
                                   game.move_state = 5
                                   self.lookahead(game, utility, permutation, depth+1)

                    #Blocking assassination/stealing can only be done by the target
                    else:
                         if game.player_list[game.target].is_alive() and game.player_list[game.target].block(game):
                              game.blocker = game.target
                              game.move_state=5
                              permutation+=1
                              self.lookahead(game, utility, permutation, depth)
          elif game.move_state == 5:
               game.move_state = 9
               for player in game.player_list:
                    if player.id == game.blocker:
                         continue
                    if player.is_alive() and player.challenge(game):
                         game.challenger = player.id
                         game.move_state = 6
          elif game.move_state == 6:
               game.win_challenge = game.resolve_block_challenge(game, game.player_list[game.blocker], game.player_list[game.challenger], game.action)
               game.move_state = 7
          elif game.move_state == 7:
               if (self.win_challenge==True): # challenger must reveal a card
                    game.player_list[game.challenger].flip_card(game)
                    if self.lives == 1:
                         utility -= 30
                    elif self.lives == 0:
                         utility -= 100
                    game.move_state = 9 # move doesn't get executed
               else: # blocker must reveal a card
                    game.player_list[game.blocker].flip_card(game)
                    if game.player_list[game.blocker].lives == 1:
                         utility += 30
                    elif game.player_list[game.blocker].lives == 0:
                         utility += 100
                    game.move_state = 8 # move does get executed
          elif game.move_state == 8:
               game.move_state = 9
               permutation += 1
               if game.action == 'Income':
                    self.coins += 1
                    utility += 1
                    (temp1, temp2) = self.lookahead(game, utility, permutation, depth)
               elif game.action == 'Coup':
                    self.coins -= 7
                    utility -= 7
                    game.player_list[game.target].flip_card(game)
                    
                    if game.player_list[game.target].lives() == 1:
                         utility += 30
                    elif game.player_list[game.target].lives() == 0:
                         utility += 100
               elif game.action == 'Foreign Aid':
                    self.coins += 2
                    utility += 2
               elif game.action == 'Tax':
                    self.coins += 3
                    utility += 3
               elif game.action == 'Assassinate':
                    self.coins -= 3
                    if game.player_list[game.target].is_alive():
                         game.player_list[game.target].flip_card(game)
                         if game.player_list[game.target].lives() == 1:
                              utility += 30
                         elif game.player_list[game.target].lives() == 0:
                              utility += 100
               elif self.action == 'Steal':
                    steal = min(game.player_list[game.target].coins, 2)
                    game.player_list[game.target].coins -= steal
                    self.coins += steal
                    utility += steal
               #need to implement exchange
          elif game.move_state == 9:
               game.move_state = 0
               alive_players = 0
               for player in self.player_list:
                    if(player.is_alive()):
                         alive_players += 1 
               # game.current_player = (self.current_player + 1) % self.num_players
               # while not self.player_list[self.current_player].is_alive():
               #      self.current_player = (self.current_player + 1) % self.num_players
               if not alive_players>1:
                    for player in self.player_list:
                         if(player.is_alive()):
                              game.winner = player.id
                    if self.id == game.winner:
                         utility += 300
               return (utility, permutation)

     def take_action(self, game:Game):
          valid_moves = []
          wins_per_move = []
          for move in self.moves:
               if (move == 'Coup' and self.coins < 7) or (move == 'Assassinate' and self.coins < 3):
                    continue
               if move in self.need_target:
                    for target in range(0, len(game.player_list)):
                         if move == 'Steal' and game.player_list[target].coins == 0:
                              continue
                         if target != self.id and game.player_list[target].is_alive():
                              valid_moves.append((move, target))
               else:
                    valid_moves.append((move, self.id))

          if(self.coins>=10):
               valid_moves = []
               for target in range(0, len(game.player_list)):
                    if target != self.id and game.player_list[target].is_alive():
                         valid_moves.append(('Coup',target))
          
          for (move, target) in valid_moves:
               utility = 0
               permutations = 0

               test_game = copy.deepcopy(game)
               test_game.action = move
               test_game.target = target
               test_game.move_state = 1
               self.lookahead(test_game, utility, permutations, 1)
               
          return (move, target)

     def challenge(self, game:Game):
          true_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               replacement = RandomAgent(self.id)
               replacement.lives = self.lives
               replacement.coins = self.coins
               replacement.cards = copy.deepcopy(self.cards)

               test_game.player_list[self.id]=replacement
               test_game.challenger = self.id
               if game.move_state==1:
                    test_game.move_state = 2
               else:
                    test_game.move_state = 6
               if test_game.run_game() == self.id:
                    true_wins = true_wins+1
          false_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               replacement = RandomAgent(self.id)
               replacement.lives = self.lives
               replacement.coins = self.coins
               replacement.cards = copy.deepcopy(self.cards)

               test_game.player_list[self.id]=replacement
               if game.move_state==1:
                    test_game.move_state = 4
               else:
                    test_game.move_state = 9
               if test_game.run_game() == self.id:
                    false_wins = false_wins+1
          selection = True
          if false_wins>true_wins:
               selection = False
          return selection

     def block(self, game:Game):
          true_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               replacement = RandomAgent(self.id)
               replacement.lives = self.lives
               replacement.coins = self.coins
               replacement.cards = copy.deepcopy(self.cards)

               test_game.player_list[self.id]=replacement
               test_game.blocker = replacement.id
               test_game.move_state = 5
               if test_game.run_game() == self.id:
                    true_wins = true_wins+1
          false_wins = 0
          for i in range(100):
               test_game = copy.deepcopy(game)
               replacement = RandomAgent(self.id)
               replacement.lives = self.lives
               replacement.coins = self.coins
               replacement.cards = copy.deepcopy(self.cards)

               test_game.player_list[self.id]=replacement
               test_game.move_state = 8
               if test_game.run_game() == self.id:
                    false_wins = false_wins+1
          selection = True
          if false_wins>true_wins:
               selection = False
          return selection
          
     def flip_card(self, game:Game): # still random
          super().flip_card(game)
          if self.cards[0].is_revealed and self.cards[1].is_revealed:
               return
          if self.cards[0].is_revealed:
               self.cards[1].life_lost()
               return
          elif self.cards[1].is_revealed:
               self.cards[0].life_lost
               return
          else: # could reveal either card
               zero_wins = 0
               for i in range(100):
                    test_game = copy.deepcopy(game)
                    replacement = RandomAgent(self.id)
                    replacement.lives = self.lives
                    replacement.coins = self.coins
                    replacement.cards = copy.deepcopy(self.cards)
                    replacement.cards[0].life_lost
                    test_game.player_list[self.id] = replacement

                    if game.move_state==3:
                         if game.win_challenge==True:
                              test_game.move_state = 4
                         else:
                              test_game.move_state = 9
                    elif game.move_state==7:
                         if game.win_challenge==True:
                              test_game.move_state = 9
                         else:
                              test_game.move_state = 8
                    else: # move_state is 8
                         test_game.move_state = 9

                    if test_game.run_game() == self.id:
                         zero_wins = zero_wins+1
               one_wins = 0
               for i in range(100):
                    test_game = copy.deepcopy(game)
                    replacement = RandomAgent(self.id)
                    replacement.lives = self.lives
                    replacement.coins = self.coins
                    replacement.cards = copy.deepcopy(self.cards)
                    replacement.cards[1].life_lost

                    test_game.player_list[self.id]=replacement
                    if game.move_state==3:
                         if game.win_challenge==True:
                              test_game.move_state = 4
                         else:
                              test_game.move_state = 9
                    elif game.move_state==7:
                         if game.win_challenge==True:
                              test_game.move_state = 9
                         else:
                              test_game.move_state = 8
                    else: # move_state is 8
                         test_game.move_state = 9
                    if test_game.run_game() == self.id:
                         one_wins = one_wins+1
               if one_wins>zero_wins:
                    self.cards[1].life_lost
               else:
                    self.cards[0].life_lost

     def exchange(self, game:Game, new_cards:list) -> list: # this is still random
          #case 1 : 2 lives 
          card_list = list()
          card_list += new_cards

          to_pop = -1
          for i in range(len(self.cards)):
               if not self.cards[i].is_revealed:
                    card_list.append(self.cards[i])
                    to_pop = i

          for _ in range(self.lives):
               self.cards.append(card_list.pop(random.randint(0, len(new_cards)-1)))
          
          for i in range(1, -1, -1):
               if not self.cards[i].is_revealed:
                    self.cards.pop(i)

          return card_list

     def __repr__(self):
          super().__repr__()


