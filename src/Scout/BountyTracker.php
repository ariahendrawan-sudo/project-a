<?php

namespace App\Scout;

use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Cache;
use App\Models\Issue;

class BountyTracker
{
    protected string $apiUrl;
    protected array $bountyCacheKey = 'bounty:scores';

    public function __construct(string $apiUrl = 'https://api.github.com/repos/ariahendrawan-sudo/project-a/issues')
    {
        $this->apiUrl = $apiUrl;
    }

    /**
     * Fetch and cache bounty scores from GitHub issues.
     */
    public function fetchBountyScores(): array
    {
        $cached = Cache::get($this->bountyCacheKey);

        if ($cached) {
            return $cached;
        }

        $issues = $this->fetchIssues();
        $scores = $this->calculateScores($issues);

        Cache::put($this->bountyCacheKey, $scores, now()->addHours(24));
        return $scores;
    }

    /**
     * Calculate bounty scores based on issue metadata.
     */
    protected function calculateScores(array $issues): array
    {
        $scores = [];

        foreach ($issues as $issue) {
            $score = $this->calculateIssueScore($issue);
            $scores[$issue['number']] = [
                'score' => $score,
                'amount' => $issue['amount'] ?? null,
                'comments' => $issue['comments'] ?? 0,
            ];
        }

        return $scores;
    }

    /**
     * Calculate individual issue score.
     */
    protected function calculateIssueScore(array $issue): float
    {
        $baseScore = $issue['score'] ?? 0;
        $commentBonus = min(($issue['comments'] ?? 0) * 0.05, 2.0);
        $amountBonus = ($issue['amount'] ?? 0) > 0 ? 1.0 : 0;

        return round($baseScore + $commentBonus + $amountBonus, 2);
    }

    /**
     * Fetch raw issue data from GitHub API.
     */
    protected function fetchIssues(): array
    {
        $response = file_get_contents($this->apiUrl);
        $issues = json_decode($response, true);

        if (json_last_error() !== JSON_ERROR_NONE) {
            Log::error('Failed to fetch bounty issues: ' . json_last_error_msg());
            return [];
        }

        return $issues['data'] ?? [];
    }
}