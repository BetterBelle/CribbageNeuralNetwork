from src.card import Card, Face
import itertools



class Hand():
    def __init__(self, cards : list[Card]=None):
        self._cards = list() if cards == None else cards

    def __str__(self) -> str:
        s = '[Hand: '
        for card in self.cards:
            s += str(card) + ' '
        return s + ']'

    def __repr__(self) -> str:
        return str(self)

    def _score_fifteens(self) -> int:
        """
        Scores all possible combinations summing to 15 in the hand
        """
        score = 0
        for n in range(1, len(self.cards) + 1):
            for combination in list(itertools.combinations(self.cards, n)):
                if sum(combination) == 15:
                    score += 2
        return score

    def _score_pairs(self) -> int:
        """
        Scores all possible combinations of a pair in the hand
        """
        score = 0
        for combination in list(itertools.combinations(self.cards, 2)):
            if combination[0] == combination[1]:
                score += 2
        return score

    def _score_runs(self) -> int:
        """
        Scores any runs in the hand
        """
        score = 0
        card_faces = [card.rank for card in self.cards]
        for i in range(5, 2, -1):
            if len(card_faces) >= i and score == 0:
                for combination in list(itertools.combinations(card_faces, i)):
                    run = True
                    combination = list(combination)
                    combination.sort()
                    for card in range(len(combination)):
                        if combination[0] != combination[card] - card:
                            run = False
                    if run:
                        score += i

        return score

    def _score_flush(self) -> int:
        """
        Scores flushes in hand, including the rule for a start card, wherein if the start card matches the suit of all cards in hand you get
        5 points instead of just 4, but it doesn't count if you get a flush of 4 with the start card. 
        """
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
        """
        Scores a nob; if the hand contains a Jack and it's suit matches the top card (only if the hand is size 5)
        """
        score = 0
        ### If we have a 5 card hand that means we can score a nob, last card is startcard
        if len(self.cards) == 5:
            for card in self.cards[:-1]:
                if card.face == Face.JACK and card.suit == self.cards[-1].suit:
                    score += 1
        return score

    @property
    def score(self) -> int:
        """
        Return the score of the hand
        """
        ### Fully score a hand
        score = 0
        score += self._score_fifteens()
        score += self._score_flush()
        score += self._score_pairs()
        score += self._score_runs()
        score += self._score_nob()
        return score

    @property
    def cards(self) -> list[Card]:
        """
        Returns the list of cards in the hand.
        """
        return self._cards
            
    def discard(self, cards : list[Card]):
        """
        Removes the cards passed in from the hand
        """
        for card in cards:
            self.cards.remove(card)

    def add_cards(self, cards : list[Card]):
        """
        Adds the cards passed in to the hand
        """
        self.cards.extend(cards)



class PeggingPile():
    def __init__(self, cards : list[Card]=None):
        self._cards_in_play = list() if cards == None else cards
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

    def _score_value(self, value : int) -> int:
        """
        Scores two points if the current pegging piles score is equal to it. This is used for scoring 15s and the 31
        """
        score = 0
        if self.current_total == value:
            score += 2
        return score

    def _n_of_a_kind(self) -> int:
        """
        Scores 4 of a kinds, 3 of a kinds and pairs. 
        """
        score = 0
        ### Four of a kind
        if len(self.cards_in_play) >= 4:
            set_of_faces = set([card.face for card in self.cards_in_play[-4:]])
            ### They all have the same values
            if len(set_of_faces) == 1:
                score += 12
        ### Three of a kind, if we've scored a 4 of a kind, we ignore
        if len(self.cards_in_play) >= 3 and score == 0:
            set_of_faces = set([card.face for card in self.cards_in_play[-3:]])
            ### They all have the same values
            if len(set_of_faces) == 1:
                score += 6
        ### Pair, if we've score either 3 or 4 of a kind, we ignore
        if len(self.cards_in_play) >= 2 and score == 0:
            set_of_faces = set([card.face for card in self.cards_in_play[-2:]])
            ### They all have the same values
            if len(set_of_faces) == 1:
                score += 2

        return score

    def _score_runs(self) -> int:
        """
        Scores runs up to 10 cards
        """
        ### Not sure what the maximum amount of cards can be in play where a long straight is possible, but will assume it's 10
        score = 0
        for i in range(10, 2, -1):
            ### If you've already scored, that means you've gotten the maximum amount of points for your run, so just keep iterating
            if len(self.cards_in_play) >= i and score == 0:
                check_cards = sorted([card.rank for card in self.cards_in_play])[-i:]
                if (check_cards[-1].rank - len(check_cards) + 1 == check_cards[0].rank):
                    score += i

        return score
        
    @property
    def cards_in_play(self) -> list[Card]:
        """
        Returns the list of cards currently in play
        """
        return self._cards_in_play

    @property
    def dead_cards(self) -> list[Card]:
        """
        Returns the list of cards currently not in play
        """
        return self._dead_cards

    @property
    def current_total(self) -> int:
        """
        Returns the current value of the pegging pile, for purposes of keeping track if the score has reached 31
        """
        stack_total = 0
        for card in self.cards_in_play:
            stack_total += card
        return stack_total

    @property
    def score(self) -> int:
        """
        Returns the score of the pegging pile
        """
        score = 0
        score += self._n_of_a_kind()
        score += self._score_value(15)
        score += self._score_value(31)
        score += self._score_runs()
        return score

    def end_current_play(self):
        """
        Sends all current cards in play to the pile of cards not in play
        """
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

    def end_pegging(self) -> list[Card]:
        """
        Sends all cards to the dead pile, wipes the dead pile and returns the cards that were dead.
        """
        self.end_current_play()
        dead_cards = self.dead_cards.copy()
        self.dead_cards.clear()
        return dead_cards