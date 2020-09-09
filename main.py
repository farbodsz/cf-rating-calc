#!/usr/bin/env python3
"""Script to calculate rating changes for Codeforces virtual contests.

The algorithm used for rating changes is the same as used on Codeforces. See
Mike Mirzayanov's blog entries:
 - Original Rating System (2010): https://codeforces.com/blog/entry/102
 - Updated Rating System (2015): https://codeforces.com/blog/entry/20762
 
"""

from sys import stdout

import requests
from docopt import docopt

from datamodels import (
    Party,
    StandingsRow,
    deserialize_rating_change,
    deserialize_standings_row,
)
from ratingcalculator import calculate_rating_changes
from util import log

CODEFORCES_API_STANDINGS = "https://codeforces.com/api/contest.standings"
CODEFORCES_API_RATING_CHANGES = (
    "https://codeforces.com/api/contest.ratingChanges"
)

VIRTUAL_USER_PARTY = Party(("{VIRTUAL_USR}",))


def fetch_rating_changes(contestid):
    """Gets a list of RatingChange objects for the contest with contestid."""
    r = requests.get(
        CODEFORCES_API_RATING_CHANGES, {"contestId": contestid}
    ).json()
    if r["status"] != "OK":
        log("Failed to retrieve rating changes.")
        return

    data = r["result"]
    rating_changes = []
    for row in data:
        rchange_row = deserialize_rating_change(row)
        rating_changes.append(rchange_row)
    return rating_changes


def fetch_standings(contestid):
    """Gets a list of StandingsRow objects for the contest with contestid."""
    r = requests.get(CODEFORCES_API_STANDINGS, {"contestId": contestid}).json()
    if r["status"] != "OK":
        log("Failed to retrieve contest standings.")
        return

    data = r["result"]["rows"]
    standings = []
    for row in data:
        standings_row = deserialize_standings_row(row)
        standings.append(standings_row)
    return standings


def add_vusr_to_standings(standings, vusr_points, vusr_penalty):
    """Adds the virtual user to the standings in the position where they would
    be if he/she had participated in the contest live.

    Arguments:
      standings     list of standings from the contest
      vusr_points   points the user obtained in the virtual contest
      vusr_penalty  penalty the user obtained in the virtual contest

    Returns:
      the updated list of standings (StandingsRow instances)
    """
    updated_standings = []
    inserted_vusr = False

    def should_insert_vusr(curr):
        if inserted_vusr:
            return False
        if vusr_points == curr.points:
            return penalty <= curr.penalty
        else:
            return vusr_points > curr.points

    for row in standings:
        if should_insert_vusr(row):
            vusr_standing = StandingsRow(
                VIRTUAL_USER_PARTY, row.rank, vusr_points, vusr_penalty,
            )
            updated_standings.append(row)
            inserted_vusr = True
        updated_standings.append(row)

    return updated_standings


def main(contestid, points, penalty, old_rating):
    """Main function for the script.

    Fetches ratings and rating changes, updates the standings with the virtual
    user's position, and calculates the new rating changes.

    Returns:
      an integer, delta, the virtual user's rating change
    """
    prev_ratings_dict = {}  # user handles -> old ratings

    log("Fetching rating changes for contest...")
    for change in fetch_rating_changes(contestid):
        prev_ratings_dict[change.handle] = change.old_rating

    # Add virtual user
    prev_ratings_dict[VIRTUAL_USER_PARTY.handles[0]] = old_rating

    log("Fetching contest standings...")
    standings = fetch_standings(contestid)
    updated_standings = add_vusr_to_standings(standings, points, penalty)

    # Create a dict of rating changes
    log("Calculating rating changes...")
    results = calculate_rating_changes(prev_ratings_dict, updated_standings)

    for k, v in results.items():
        print(str(k) + " -> " + str(v))

    return results[VIRTUAL_USER_PARTY]


if __name__ == "__main__":
    command_doc = """Codeforces Virtual Rating Calculator.

    Calculates your rating change in a Codeforces virtual contest and outputs it
    to stdout.

    Usage:
      cf-rating-calc.py <contestId> <points> <penalty> <oldRating>

    Arguments:
      contestId     ID of the contest. It is not the round number. It can be
                    seen in the contest URL of a Codeforces. For example, 
                    /contest/566/status
      points        number of points
      penalty       penalty
      oldRating     your rating

    """
    arguments = docopt(command_doc)

    contestid = int(arguments["<contestId>"])
    points = int(arguments["<points>"])
    penalty = int(arguments["<penalty>"])
    old_rating = int(arguments["<oldRating>"])

    delta = main(contestid, points, penalty, old_rating)
    stdout.write(str(delta))
