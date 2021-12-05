#Actions: Income, Foreign Aid, Tax, Steal, Assassinate, Exchange, Coup
import random
class Card:
    def __init__(self):
        self.is_revealed = False
        self.valid_actions = None
        self.can_block = None

    def life_lost(self):
        self.is_revealed = True

    def __repr__(self):
        ans = type(self).__name__
        if self.is_revealed:
            ans += ' revealed'
        else:
            ans += ' hidden'
        return ans
    

class Duke(Card):
    def __init__(self):
        super().__init__()
        self.valid_actions = 'Tax'
        self.can_block = 'Foreign Aid'


class Captain(Card):
    def __init__(self):
        super().__init__()
        self.valid_actions = 'Steal'
        self.can_block  = 'Steal'
    

class Ambassador(Card):
    def __init__(self):
        super().__init__()
        self.valid_actions = 'Exchange'
        self.can_block = 'Steal'

class Assassin(Card):
    def __init__(self):
        super().__init__()
        self.valid_actions = 'Assassinate'

class Contessa(Card):
    def __init__(self):
        super().__init__()
        self.can_block = 'Assassinate'

class Deck:
    def __init__(self):
        self.cards = list()
        for _ in range(3):
            self.cards.append(Duke())
            self.cards.append(Captain())
            self.cards.append(Ambassador())
            self.cards.append(Assassin())
            self.cards.append(Contessa())

        random.shuffle(self.cards)

    def deal(self) -> Card:
        #print(f'Deck has {len(self.cards) - 1} cards after deal')
        return self.cards.pop(0)
    
    def return_cards(self, to_add:list):
        self.cards += to_add
        #print(f'Deck has {len(self.cards)} cards after return')
        random.shuffle(self.cards)


if __name__ == '__main__':
    Deck()