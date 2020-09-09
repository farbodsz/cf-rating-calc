"""Module which implements the Codeforces Rating Calculator.

This module is essentially a port of Mike Mirzayanov's algorithm to Python.
See https://codeforces.com/contest/1/submission/13861109
"""

import math

from datamodels import Party
from util import log


class Contestant:
    party: Party
    rank: int
    points: int
    rating: int  # previous rating

    seed: float
    need_rating: int
    delta: int

    def __init__(self, party, rank, points, previous_rating):
        self.party = party
        self.rank = rank
        self.points = points
        self.rating = previous_rating

        self.seed = 0.0
        self.need_rating = 0
        self.delta = 0


def validate_deltas(contestants):
    """Compares deltas of all pairs of contestants, raising an exception if
    invalid."""
    sort_by_points_desc(contestants)

    def ensure(expr, is_first_rating, party1, party2):
        """Raises an exception if expr is false. The error message is generated
        from the remaining parameters."""
        if not expr:
            num = "First" if is_first_rating else "Second"
            msg = f"{num} rating invariant failed: {party1} vs {party2}."
            raise Exception(msg)

    for i in range(len(contestants)):
        for j in range(i + 1, len(contestants)):
            if contestants[i].rating > contestants[j].rating:
                check = (
                    contestants[i].rating + contestants[i].delta
                    >= contestants[j].rating + contestants[j].delta
                )
                ensure(check, True, contestants[i].party, contestants[j].party)

            if contestants[i].rating < contestants[j].rating:
                if contestants[i].delta < contestants[j].delta:
                    print(1)  # TODO why
                check = contestants[i].delta >= contestants[j].delta
                ensure(check, False, contestants[i].party, contestants[j].party)


def get_seed(contestants, rating, seed_cache):
    """Returns a float."""
    if rating in seed_cache:
        return seed_cache[rating]

    extra = Contestant(None, 0, 0, rating)
    result = 1.0
    for other in contestants:
        result += get_elo_win_probability(other.rating, extra.rating)
    seed_cache[rating] = result
    return result


def get_rating_to_rank(contestants, rank, seed_cache):
    left = 1
    right = 8000
    while right - left > 1:
        mid = (left + right) // 2
        if get_seed(contestants, mid, seed_cache) < rank:
            right = mid
        else:
            left = mid
    return left


def get_elo_win_probability(ra, rb):
    """Returns the Elo win probability (float) with the given ratings ra, rb."""
    return 1.0 / (1.0 + math.pow(10, (rb - ra) / 400.0))


def sort_by_points_desc(contestants):
    contestants.sort(key=lambda x: x.points, reverse=True)


def sort_by_rating_desc(contestants):
    contestants.sort(key=lambda x: x.rating, reverse=True)


def reassign_ranks(contestants):
    sort_by_points_desc(contestants)

    first = 0
    points = contestants[0].points

    for i in range(1, len(contestants)):
        if contestants[i].points < points:
            for j in range(first, i):
                contestants[j].rank = i
            first = i
            points = contestants[i].points

    rank = len(contestants)
    for j in range(first, len(contestants)):
        contestants[j].rank = rank


def process(contestants):
    """Processes rating changes of the given list of contestants."""
    if not contestants:
        return

    log("Reassigning ranks...")
    reassign_ranks(contestants)

    # Caches the calculated seed for a given rating
    seed_cache = {}

    log("Calculating deltas...")
    for contestant in contestants:
        rating = contestant.rating
        contestant.seed = get_seed(contestants, rating, seed_cache) - 0.5
        mid_rank = math.sqrt(contestant.rank * contestant.seed)
        contestant.need_rating = get_rating_to_rank(
            contestants, mid_rank, seed_cache
        )
        contestant.delta = (contestant.need_rating - rating) // 2

    sort_by_rating_desc(contestants)
    log("Adjusting sums...")

    # Total sum should not be more than zero
    def total_sum_not_more_than_zero():
        sum = 0
        for c in contestants:
            sum += c.delta
        inc = -sum // len(contestants) - 1
        for c in contestants:
            c.delta += inc

    total_sum_not_more_than_zero()

    # Sum of top-4*sqrt should be adjusted to zero
    def adjust_sum():
        sum = 0
        calc = int(4 * round(math.sqrt(len(contestants))))
        zero_sum_count = min(calc, len(contestants))
        for i in range(zero_sum_count):
            sum += contestants[i].delta
        inc = min(0, max(-sum // zero_sum_count, -10))
        for c in contestants:
            c.delta += inc

    adjust_sum()

    log("Validating deltas...")
    validate_deltas(contestants)


def calculate_rating_changes(previous_ratings, standings):
    """Returns a dict of competing parties with their corresponding rating
    changes (delta, as an integer).

    Arguments:
      previous_ratings    dict of handles with their corresponding previous
                          rating
      standings           a list of StandingsRow including the virtual user's
                          participation

    Returns:
      dict of parties with their corresponding rating change
    """
    contestants = []

    # Construct list of Contestants
    log(f"Constructing list of {len(standings)} contestants...")
    for row in standings:
        rank = row.rank
        party = row.party
        c = Contestant(
            party, rank, row.points, previous_ratings[party.handles[0]]
        )
        contestants.append(c)

    # List will be modified by process function (passed by reference)
    process(contestants)

    rating_changes = {}
    for c in contestants:
        rating_changes[c.party] = c.delta
    return rating_changes
