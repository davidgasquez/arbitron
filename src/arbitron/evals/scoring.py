def kendall_tau(ranking1, ranking2):
    """Compute Kendall's Tau correlation manually."""
    n = len(ranking1)
    concordant = 0
    discordant = 0

    for i in range(n):
        for j in range(i + 1, n):
            # Get items at positions i and j in ranking2 (real ranking)
            item_i = ranking2[i]
            item_j = ranking2[j]

            # Find their positions in ranking1 (arbitron ranking)
            pos1_i = ranking1.index(item_i)
            pos1_j = ranking1.index(item_j)

            # Check if relative order is preserved
            if pos1_i < pos1_j:  # Same order as in ranking2
                concordant += 1
            else:  # Different order
                discordant += 1

    total_pairs = n * (n - 1) / 2
    tau = (concordant - discordant) / total_pairs
    return tau
