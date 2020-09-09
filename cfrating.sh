#!/usr/bin/env bash
#
# Script which provides a more user-friendly interface to the Codeforces rating
# calculator (Python script).
#
# The user can interactively input parameters and the output is nicely
# formatted.

# Colours
COLOR_NONE='\033[0m'
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'

printf "Codeforces Virtual Rating Calculator:\n\n"

read -p "  contestId: " contestId
read -p "  points:    " points
read -p "  penalty:   " penalty
read -p "  oldRating: " oldRating

printf "\n"

ratingChange=$(python3 ./main.py $contestId $points $penalty $oldRating)

color=COLOR_NONE
if [[ "$ratingChange" -lt 0 ]]; then
  color=$COLOR_RED
fi
if [[ "$ratingChange" -gt 0 ]]; then
  color=$COLOR_GREEN
  ratingChange="+${ratingChange}"
fi

printf "\n  Rating Change:\n\n"
printf "        ${color}${ratingChange}${COLOR_NONE}\n\n"
