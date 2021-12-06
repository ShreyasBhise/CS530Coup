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
                    replacement = RandomAgent(self.id)
                    replacement.lives = self.lives
                    replacement.coins = self.coins
                    replacement.cards = copy.deepcopy(self.cards)

                    test_game.player_list[self.id]=replacement
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
               self.cards[0].life_lost()
               return
          else: # could reveal either card
               zero_wins = 0
               for i in range(100):
                    #print('------------------------' + str(self.lives))
                    test_game = copy.deepcopy(game)
                    replacement = RandomAgent(self.id)
                    replacement.lives = self.lives
                    replacement.coins = self.coins
                    replacement.cards = copy.deepcopy(self.cards)
                    replacement.cards[0].life_lost()
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
                    replacement.cards[1].life_lost()

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