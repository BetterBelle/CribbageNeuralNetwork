from abc import ABCMeta, abstractmethod
from scoring import Hand
from card import Card, Deck
import random
import tensorflow as tf



class Player(metaclass=ABCMeta):
    """Abstract Base Class for a Player"""
    def __init__(self, name='John Doe'):
        self._name = name
        self._hand = Hand()
        self._score = 0

    def __str__(self) -> str:
        return '[Player: ' + self.name + ']'

    @property
    def name(self) -> str:
        return self._name

    @property
    def hand(self) -> Hand:
        return self._hand

    @property
    def score(self) -> int:
        return self._score

    def get_cards(self, cards : list):
        self._hand.add_cards(cards)

    @abstractmethod
    def select_discards(self) -> list:
        """
        Select cards to place in the crib.
        """
        raise NotImplementedError()

    @abstractmethod
    def select_peg_card(self) -> Card:
        """
        Select card to play into the pegging pile
        """
        raise NotImplementedError()



class RandomPlayer(Player):
    def select_discards(self) -> list:
        cards_to_discard = random.sample(self.hand, 2)
        self._hand.discard(cards_to_discard)
        return cards_to_discard

    def select_peg_card(self) -> Card:
        card_to_play = random.choice(self.hand)
        self._hand.discard([card_to_play])
        return card_to_play



class HumanPlayer(Player):
    def present_cards_for_selection(self, num_cards=1):
        """
        Text representation of the hand for the user to select cards to play/discard
        """
        selected_cards = []
        while len(selected_cards) < num_cards:
            selected_cards = []
            s = ''
            for i, card in enumerate(self.hand.cards):
                s += '(' + str(i + 1) + ') ' + str(card) + '\n'

            print('Here are your cards:\n' + s)
            selection = input('Select ' + str(num_cards) + ' cards: ')
            card_indexes = [int(s) for s in selection.split(' ') if s.isdigit()]
            for i in card_indexes:
                if i < 1 or i > len(self.hand.cards):
                    print(str(i) + ' is an invalid selection.')
                else:
                    selected_cards.append(self.hand.cards[i-1])

        self._hand.discard(selected_cards)
        return selected_cards

    def select_discards(self) -> list:
        return self.present_cards_for_selection(2)

    def select_peg_card(self) -> Card:
        return self.present_cards_for_selection(1)

