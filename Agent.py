class Agent:
     def __init__(self, id):
          self.lives = 2
          self.id = id
          self.coins = 2
          self.cards = []
          self.valid_moves = {'Income', 'Foreign Aid', 'Coup'}
     
     def get_card(self, card):
          self.cards.append(card)

     def take_action(self, player_list:list):
          return

     def challenge(self, action:tuple, player_list:list):
          return False

     def block(self, action:tuple, player_list:list):
          return False
          
     def flip_card(self):
          self.lives -= 1

     def is_alive(self):
          return self.lives > 0

     def exchange(self, new_cards:list) -> list:
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
     
     def take_action(self, player_list:list):
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
               if action in self.need_target:
                    while target == self.id or not player_list[target].is_alive() or player_list[target].coins == 0:
                         target = random.randint(0, len(player_list) - 1)
               invalid = False
          return (action, target)

     def challenge(self, action:tuple, player_list:list):
          return random.choice([True,False])

     def block(self, action:tuple, player_list:list):
          return random.choice([True,False])
          
     def flip_card(self):
          card = self.cards[random.randint(0, 1)]
          while card.is_revealed:
               card = self.cards[random.randint(0, 1)]
          card.life_lost()

          super().flip_card()

     def exchange(self, new_cards:list) -> list:
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
          
          to_discard = list()
          for i in range(1, -1, -1):
               if not self.cards[i].is_revealed:
                    to_discard.append(self.cards.pop(i))

     
          return to_discard



     def __repr__(self):
          super().__repr__()
          
               
          