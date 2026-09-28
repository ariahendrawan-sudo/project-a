<?php

namespace App\Scout;

use App\Models\Issue;
use Illuminate\Support\Facades\Log;

class BountyScout
{
    protected BountyTracker $tracker;

    public function __construct(BountyTracker $tracker)
    {
        $this->tracker = $tracker;
    }

    /**
     * Score and rank issues based on bounty criteria.
     */
    public function rankIssues(): array
    {
        $scores = $this->tracker->fetchBountyScores();
        $ranked = [];

        foreach ($scores as $issueNumber => $scoreData) {
            $ranked[] = [
                'number' => $issueNumber,
                'score' => $scoreData['score'],
                'amount' => $scoreData['amount'],
                'comments' => $scoreData['comments'],
            ];
        }

        usort($ranked, fn($a, $b) => $b['score'] <=> $a['score']);
        return $ranked;
    }

    /**
     * Assign bounty to the highest-scoring issue.
     */
    public function assignBounty(): ?Issue
    {
        $ranked = $this->rankIssues();
        $topIssue = $ranked[0] ?? null;

        if (!$topIssue) {
            return null;
        }

        $issue = Issue::find($topIssue['number']);
        $issue->update([
            'bounty_score' => $topIssue['score'],
            'bounty_amount' => $topIssue['amount'],
            'bounty_assigned' => true,
        ]);

        return $issue;
    }
}