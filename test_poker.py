import poker


def test_rank_numbers():
    cards = [
        poker.Card(suit, rank)
        for suit in ["C"]
        for rank in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    ]
    assert [card.rank_str for card in cards] == [
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "Ten",
        "Jack",
        "Queen",
        "King",
        "Ace",
    ]


def test_shuffle_cardstack():
    cards = [
        poker.Card(suit, rank)
        for suit in ["C", "D", "H", "S"]
        for rank in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    ]
    shuffled_stack = poker.Cardstack()
    assert cards != shuffled_stack.cards


def test_take_cards():
    cardstack = poker.Cardstack()
    top_3_cards = cardstack.cards[:3]
    taken_cards = cardstack.take_cards(3)
    assert top_3_cards == taken_cards


def test_take_cards_removed():
    cardstack = poker.Cardstack()
    top_3_cards = cardstack.cards[:3]
    cardstack.take_cards(3)
    assert top_3_cards not in cardstack.cards


def test_deal_cards():
    Alice = poker.Player(100, name="Alice")
    Ben = poker.Player(100, name="Ben")
    Chris = poker.Player(100, name="Chris")
    first_game = poker.Table(players=[Alice, Ben, Chris], big_blind=10)
    first_game.deal_cards()

    assert all([len(player.hand) == 2 for player in first_game.players])


def test_seat_players():
    Alice = poker.Player(100, name="Alice")
    Ben = poker.Player(100, name="Ben")
    Chris = poker.Player(100, name="Chris")
    first_game = poker.Table(players=[Alice, Ben, Chris])

    assert all(
        [
            position in [player.seat for player in first_game.players]
            for position in list(range(3))
        ]
    )


def test_take_blinds():
    Alice = poker.Player(100, name="Alice")
    Ben = poker.Player(100, name="Ben")
    Chris = poker.Player(100, name="Chris")
    first_game = poker.Table(players=[Alice, Ben, Chris], big_blind=10)
    first_game.take_blinds()
    big_blind = [player for player in first_game.players if player.seat == 1][0]
    small_blind = [player for player in first_game.players if player.seat == 2][0]

    assert all([big_blind.stack == 90, small_blind.stack == 95])


def test_change_dealer():
    Alice = poker.Player(100, name="Alice")
    Ben = poker.Player(100, name="Ben")
    Chris = poker.Player(100, name="Chris")
    first_game = poker.Table(players=[Alice, Ben, Chris], big_blind=10)
    should_be_next_dealer = [
        player for player in first_game.players if player.seat == 1
    ][0]
    first_game.change_dealer()

    assert should_be_next_dealer == first_game.dealer


def test_eliminate_player():
    Alice = poker.Player(100, name="Alice")
    Ben = poker.Player(100, name="Ben")
    Chris = poker.Player(100, name="Chris")
    first_game = poker.Table(players=[Alice, Ben, Chris], big_blind=10)
    player_seat_zero = [player for player in first_game.players if player.seat == 0][0]
    player_seat_one = [player for player in first_game.players if player.seat == 1][0]
    player_seat_two = [player for player in first_game.players if player.seat == 2][0]
    first_game.eliminate_player(player_seat_one)

    one_out_of_players = player_seat_one not in first_game.players
    one_in_eliminated = first_game.eliminated == [player_seat_one]
    player_seat_zero_stays = player_seat_zero.seat == 0
    player_seat_two_lowered = player_seat_two.seat == 1

    assert all(
        [
            one_out_of_players,
            one_in_eliminated,
            player_seat_zero_stays,
            player_seat_two_lowered,
        ]
    )


def test_rules_high_card():
    cards = [
        poker.Card("C", 14),
        poker.Card("C", 5),
        poker.Card("S", 10),
        poker.Card("H", 2),
        poker.Card("D", 8),
    ]
    ruleset = poker.Rules(big_blind=10)
    high_card = ruleset.high_card(cards)

    assert high_card == cards[0]


def test_rules_pair():
    cards = [
        poker.Card("C", 14),
        poker.Card("C", 5),
        poker.Card("S", 14),
        poker.Card("H", 2),
        poker.Card("D", 8),
    ]
    ruleset = poker.Rules(big_blind=10)
    pair, rest, string = ruleset.x_of_a_kind(cards)

    assert all(
        [
            pair == [cards[0], cards[2]],
            rest == [cards[1], cards[3], cards[4]],
            string == "Pair",
        ]
    )


def test_rules_three_of_a_kind():
    cards = [
        poker.Card("C", 14),
        poker.Card("C", 5),
        poker.Card("S", 14),
        poker.Card("H", 14),
        poker.Card("D", 8),
    ]
    ruleset = poker.Rules(big_blind=10)
    threes, rest, string = ruleset.x_of_a_kind(cards)

    assert all(
        [
            threes == [cards[0], cards[2], cards[3]],
            rest == [cards[1], cards[4]],
            string == "Three of a Kind",
        ]
    )


def test_rules_four_of_a_kind():
    cards = [
        poker.Card("C", 14),
        poker.Card("D", 14),
        poker.Card("S", 14),
        poker.Card("H", 14),
        poker.Card("D", 8),
    ]
    ruleset = poker.Rules(big_blind=10)
    fours, rest, string = ruleset.x_of_a_kind(cards)

    assert all(
        [
            fours == [cards[0], cards[1], cards[2], cards[3]],
            rest == [cards[4]],
            string == "Four of a Kind",
        ]
    )


def test_rules_full_house():
    cards = [
        poker.Card("C", 14),
        poker.Card("D", 14),
        poker.Card("S", 8),
        poker.Card("H", 14),
        poker.Card("D", 8),
    ]
    ruleset = poker.Rules(big_blind=10)
    house, rest, string = ruleset.x_of_a_kind(cards)

    assert all([house == cards, rest == [], string == "Full House"])


def test_rules_two_pair():
    cards = [
        poker.Card("C", 14),
        poker.Card("D", 14),
        poker.Card("S", 8),
        poker.Card("H", 10),
        poker.Card("D", 8),
    ]
    ruleset = poker.Rules(big_blind=10)
    twopair, rest, string = ruleset.x_of_a_kind(cards)

    assert all(
        [
            twopair == [cards[0], cards[1], cards[2], cards[4]],
            rest == [cards[3]],
            string == "Two Pair",
        ]
    )


def test_flush():
    cards = [
        poker.Card("H", 2),
        poker.Card("H", 14),
        poker.Card("S", 8),
        poker.Card("H", 7),
        poker.Card("H", 9),
        poker.Card("H", 11),
        poker.Card("H", 8),
    ]
    ruleset = poker.Rules(big_blind=10)
    flush, string = ruleset.flush(cards)

    assert all(
        [
            flush == [cards[1], cards[5], cards[4], cards[6], cards[3]],
            string == "Flush! Ace high",
        ]
    )


def test_straight():
    cards = [
        poker.Card("H", 2),
        poker.Card("H", 14),
        poker.Card("S", 11),
        poker.Card("H", 12),
        poker.Card("S", 5),
        poker.Card("H", 10),
        poker.Card("C", 13),
    ]
    ruleset = poker.Rules(big_blind=10)
    straight, string = ruleset.straight(cards)

    assert all(
        [
            straight == [cards[1], cards[6], cards[3], cards[2], cards[5]],
            string == "Straight! Ace to Ten",
        ]
    )
