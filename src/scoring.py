from card import Card, Face, Suit
import itertools

class Hand():
    def __init__(self, cards=list):
        self._cards = cards

    def __str__(self) -> str:
        s = '[ '
        for card in self.cards:
            s += str(card) + ' '
        return s + ']'

    def __repr__(self) -> str:
        return str(self)

    def _score_fifteens(self) -> int:
        score = 0
        for n in range(1, len(self.cards) + 1):
            for combination in list(itertools.combinations(self.cards, n)):
                if sum(combination) == 15:
                    score += 2
        return score

    def _score_pairs(self) -> int:
        score = 0
        for combination in list(itertools.combinations(self.cards, 2)):
            if combination[0] == combination[1]:
                score += 2
        return score

    def _score_runs(self) -> int:
        self._cards.sort()
        score = 0
        ### Runs of four
        for combination in list(itertools.combinations(self.cards, 4)):
            combination = list(combination)
            combination.sort()
            if (combination[-1] - len(combination) + 1 == combination[0]):
                score += 4

        ### If you scored runs of 4, you won't have any runs of 3
        if score > 0:
            return score
        ### Runs of three
        for combination in list(itertools.combinations(self.cards, 3)):
            combination = list(combination)
            combination.sort()
            if (combination[-1] - len(combination) + 1 == combination[0]):
                score += 3

        return score

    def _score_flush(self) -> int:
        score = 0
        suits = [card.suit.value['value'] for card in self.cards]
        ### If we have a 5 card hand that means we're including start card
        if len(suits) == 5:
            if len(set(suits)) == 1:
                score += 5
            ### If we didn't score 5, exclude start card, then try again
            elif len(set(suits[:-1])) == 1:
                score += 4
        ### Otherwise, we have a 4 card hand
        elif len(set(suits)) == 1:
            score += 4
        return score

    def _score_nob(self) -> int:
        score = 0
        ### If we have a 5 card hand that means we score a nob
        if len(self.cards) == 5:
            startcard = self.cards[-1]
            for card in self.cards[:-1]:
                if card.face == Face.JACK:
                    if card.suit == startcard.suit:
                        score += 1
        
        return score

    @property
    def score(self) -> int:
        ### Fully score a hand
        score = 0
        score += self._score_fifteens()
        score += self._score_flush()
        score += self._score_pairs()
        score += self._score_runs()
        score += self._score_nob()
        return score

    @property
    def cards(self) -> list:
        return self._cards
            
    def discard(self, cards : list):
        for card in cards:
            self._cards.remove(card)

    def add_cards(self, cards : list):
        self._cards.extend(cards)


class PeggingPile():
    def __init__(self, cards=[]):
        self._cards_in_play = cards
        self._dead_cards = []

    def __str__(self) -> str:
        s = '[\n\tCards In Play: '
        for card in self.cards_in_play:
            s += str(card) + ' '

        s += '\n\tDead Cards: '
        for card in self.dead_cards:
            s += str(card) + ' '
        return s + '\n]'

    def __repr__(self):
        return str(self)

    def _score_value(self, value) -> int:
        score = 0
        if self.current_total == value:
            score += 2
        return score

    def _n_of_a_kind(self) -> int:
        score = 0
        ### Four of a kind
        if len(self.cards_in_play) >= 4:
            set_of_values = set([card.value for card in self.cards_in_play[-4:]])
            ### They all have the same values
            if len(set_of_values) == 1:
                score += 12
        ### Three of a kind, if we've scored a 4 of a kind, we ignore
        if len(self.cards_in_play) >= 3 and score == 0:
            set_of_values = set([card.value for card in self.cards_in_play[-3:]])
            ### They all have the same values
            if len(set_of_values) == 1:
                score += 6
        ### Pair, if we've score either 3 or 4 of a kind, we ignore
        if len(self.cards_in_play) >= 2 and score == 0:
            set_of_values = set([card.value for card in self.cards_in_play[-2:]])
            ### They all have the same values
            if len(set_of_values) == 1:
                score += 2

        return score

    def _score_runs(self) -> int:
        ### Not sure what the maximum amount of cards can be in play where a long straight is possible, but will assume it's 10
        score = 0
        for i in range(10, 1, -1):
            ### If you've already scored, that means you've gotten the maximum amount of points for your run, so just keep iterating
            if len(self.cards_in_play) >= i and score == 0:
                check_cards = sorted(self.cards_in_play)
                if (check_cards[-1] - len(check_cards) + 1 == check_cards[0]):
                    score += i

        return score
        
    @property
    def cards_in_play(self) -> list:
        return self._cards_in_play

    @property
    def dead_cards(self) -> list:
        return self._dead_cards

    @property
    def current_total(self) -> int:
        stack_total = 0
        for card in self.cards_in_play:
            stack_total += card.value
        return stack_total

    @property
    def score(self) -> int:
        score = 0
        score += self._n_of_a_kind()
        score += self._score_value(15)
        score += self._score_value(31)
        score += self._score_runs()
        return score

    def end_current_play(self):
        self._dead_cards.extend(self.cards_in_play)
        self._cards_in_play = []

    def add_to_play(self, card : Card) -> int:
        """
        Add a card to play and return the score of the new pile.
        Then, if the total is 31, send all cards to the dead card pile
        """
        if card.value + self.current_total > 31:
            raise ValueError("You cannot play that card! Please select another card.")

        score = self.score

        if self.current_total == 31:
            self.end_current_play()

        return score