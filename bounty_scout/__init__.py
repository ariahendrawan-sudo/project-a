def filter_bounties(bounties):
    filtered_bounties = []
    for bounty in bounties:
        if bounty['amount'] > 0:  # Ensure the bounty has a stated amount
            filtered_bounties.append(bounty)
    return filtered_bounties