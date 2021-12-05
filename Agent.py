import Game

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
          
               
          
class MonteCarloTreeAgent(Agent):
     pass