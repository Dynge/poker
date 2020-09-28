import math
import random
import logging

logging.basicConfig(level=logging.DEBUG)


class Player:
    def __init__(self, money: int, name="Generic"):
        """Initializes a player with a stack of money."""
        self.name = name
        self.stack = money
        self.hand = []
        self.seat = None

        logging.info(
            "Player '{}' has joined the game. They have {},- in their stack".format(
                self.name, self.stack
            )
        )

    def __repr__(self):
        return "'{}' Stack: {},-".format(self.name, self.stack)

    def bet(self, money):
        """Bets money to the table. The money is removed from the players stack"""
        money = int(money)
        if money > self.stack:
            money = self.stack
        self.stack -= money

        logging.info(
            "{} bets {},-. They have {} left in their stack.".format(
                self.name, money, self.stack
            )
        )

        return money

    def fold(self):
        """Folds the players hand, meaning their hand is empty"""
        logging.info("{} folds.".format(self.name))
        self.hand = []


class Rules:
    def __init__(self, big_blind: int):
        self.big_blind = big_blind
        self.small_blind = math.ceil(big_blind / 2)

    def high_card(self, cards):
        """Finds the highest ranked card in the selection of cards."""
        max_rank = max([card.rank for card in cards])
        highest_card = [card for card in cards if card.rank == max_rank][0]
        return highest_card

    def x_of_a_kind(self, cards):
        """Determines if there are any 'X of a kind' matches in the cards. This includes: Full House, One Pair, Two Pair, Three of a Kind and Four of a Kind"""
        scoring_cards = cards.copy()
        ranks = [card.rank for card in cards]
        counts = [ranks.count(rank) for rank in ranks]
        if 2 in counts and 3 in counts:
            rest = []
            return scoring_cards, rest, "Full House"
        max_x_of_a_kind = max(counts)

        duplicate_cards = [
            scoring_cards[index]
            for index in range(len(counts))
            if counts[index] == max_x_of_a_kind
        ]
        rest = [
            scoring_cards[index]
            for index in range(len(counts))
            if counts[index] != max_x_of_a_kind
        ]
        if len(duplicate_cards) == 4 and max_x_of_a_kind == 2:
            return duplicate_cards, rest, "Two Pair"
        elif len(duplicate_cards) == 4:
            return duplicate_cards, rest, "Four of a Kind"
        elif len(duplicate_cards) == 3:
            return duplicate_cards, rest, "Three of a Kind"
        elif len(duplicate_cards) == 2:
            return duplicate_cards, rest, "Pair"
        else:
            return duplicate_cards, rest, "Nothing"

    def flush(self, cards):
        cards = cards.copy()
        suits = [card.suit for card in cards]
        counts = [suits.count(suit) for suit in suits]
        if max(counts) >= 5:
            scoring_cards = [
                card for card in cards if card.suit == suits[counts.index(max(counts))]
            ]
            highest_flush = []
            for _ in range(5):
                highest_card = self.high_card(scoring_cards)
                highest_flush.append(highest_card)
                scoring_cards.remove(highest_card)

            return highest_flush
        else:
            return None

    def straight(self, cards):
        cards = cards.copy()

        def _next_rank(rank, iteration, cards=cards):
            ranks = [card.rank for card in cards]
            if (rank - 1) in ranks:
                iteration = _next_rank(rank - 1, iteration + 1)
                return iteration
            else:
                return iteration

        straight_counts = [_next_rank(rank=card.rank, iteration=1) for card in cards]
        if max(straight_counts) >= 5:
            highest_card_rank = cards[straight_counts.index(max(straight_counts))].rank
            highest_straight = []
            for _ in range(5):
                highest_card = [
                    card for card in cards if card.rank == highest_card_rank
                ][0]
                highest_straight.append(highest_card)
                highest_card_rank -= 1

            return highest_straight
        else:
            return None

    def best_hand(self, cards):
        cards = cards.copy()
        straight = self.straight(cards)
        flush = self.flush(cards)
        if straight and flush:
            return {
                "cards": straight,
                "hand": "StraightFlush",
                "high": straight[0].rank_str,
            }
        """
        straight flush
        four
        house
        flush
        straight
        three
        two pair
        one pair
        high card
        """


class Table(Rules):
    def __init__(self, players, big_blind=5):
        """Initialize a table with a set amount of players"""
        super().__init__(big_blind)
        self.cardstack = Cardstack()
        self.players = players
        self.eliminated = []
        self.seat_players()
        self.dealer = self.assign_first_dealer()
        self.cards_on_table = []
        self.pot = 0

    def __repr__(self):
        return "Table of {} players. Stack Sum: {},-".format(
            len(self.players), sum([player.stack for player in self.players])
        )

    def assign_first_dealer(self):
        """Assigns the player with seat = 0 as the first dealer"""
        seat_zero_player = [player for player in self.players if player.seat == 0][0]
        return seat_zero_player

    def seat_players(self):
        """Determines a random seat a the table for the players."""
        seats = [seat_position for seat_position in range(len(self.players))]
        random.shuffle(seats)
        for player in self.players:
            player.seat = seats[0]
            seats = seats[1:]

    def deal_cards(self):
        """Gives every player that is not eliminated 2 cards"""
        self.cardstack.shuffle_cards()
        [player.fold() for player in self.players]
        for iteration in range(2):
            for player in self.players:
                top_card = self.cardstack.take_cards(1)
                logging.debug("Dealing card {} to {}".format(top_card, player.name))
                [player.hand.append(card) for card in top_card]

    def take_blinds(self):
        """Takes blinds from the players to the right of dealer."""
        big_blind_position = (self.dealer.seat + 1) % len(self.players)
        small_blind_position = (self.dealer.seat + 2) % len(self.players)
        for player in self.players:
            if player.seat == big_blind_position:
                player.stack -= self.big_blind
            if player.seat == small_blind_position:
                player.stack -= self.small_blind

    def change_dealer(self):
        """Change the dealer to the person to the right (seat + 1)"""
        next_dealer = [
            player for player in self.players if player.seat == (self.dealer.seat + 1)
        ][0]
        self.dealer = next_dealer

    def eliminate_player(self, player):
        """Removes a player from the players of the table. This appends the player to the eliminated list and changes his seat position to None"""
        self.eliminated.append(player)
        self.players.remove(player)
        for remaining_player in self.players:
            if remaining_player.seat > player.seat:
                remaining_player.seat -= 1
        player.seat = None
        player.position = len(self.players)

    def next_round(self):
        if len(self.cards_on_table) == 0:
            self.cardstack.take_cards(1)
            [self.cards_on_table.append(card) for card in self.cardstack.take_cards(3)]

        if len(self.cards_on_table) == 3:
            self.cardstack.take_cards(1)
            [self.cards_on_table.append(card) for card in self.cardstack.take_cards(1)]

        if len(self.cards_on_table) == 4:
            self.cardstack.take_cards(1)
            [self.cards_on_table.append(card) for card in self.cardstack.take_cards(1)]

        if len(self.cards_on_table) == 5:
            self.deal_cards()


class Cardstack:
    def __init__(self):
        self.cards = self.new_deck()
        logging.debug(
            "Cardstack: {}".format([card.suit + card.rank_str for card in self.cards])
        )

    def __repr__(self):
        return self.__name__

    def new_deck(self):
        """Creates a new deck of cards."""
        new_deck_of_cards = [
            Card(suit, rank)
            for suit in ["C", "D", "H", "S"]
            for rank in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        ]
        return new_deck_of_cards

    def shuffle_cards(self):
        """Shuffles a list of cards"""
        self.cards = self.new_deck()
        random.shuffle(self.cards)

    def take_cards(self, n):
        """Remove n of the cards from the top of the stack"""
        cards_to_remove = self.cards[:n]
        self.cards = self.cards[n:]
        return cards_to_remove


class Card:
    def __init__(self, suit, rank):
        """Init a Card with a suit and a rank"""
        self.suit = suit
        self.rank = rank
        self.determine_hr_rank(rank)

    def __repr__(self):
        return "Card {}:{}".format(self.suit, self.rank_str)

    def determine_hr_rank(self, rank):
        """Create a human-readable rank identification, such as T, J, Q, K and A"""
        if rank in [_ + 2 for _ in range(8)]:
            rank_str = str(rank)
        elif rank == 10:
            rank_str = "Ten"
        elif rank == 11:
            rank_str = "Jack"
        elif rank == 12:
            rank_str = "Queen"
        elif rank == 13:
            rank_str = "King"
        else:
            rank_str = "Ace"

        self.rank_str = rank_str


if __name__ == "__main__":
    cards = [
        Card("H", 14),
        Card("H", 3),
        Card("S", 4),
        Card("H", 5),
        Card("H", 6),
        Card("H", 7),
        Card("H", 10),
    ]
    ruleset = Rules(big_blind=10)
    straight = ruleset.straight(cards)
    logging.debug(straight)
