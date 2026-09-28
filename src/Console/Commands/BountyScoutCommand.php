<?php

namespace App\Console\Commands;

use App\Scout\BountyScout;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

class BountyScoutCommand extends Command
{
    protected $signature = 'bounty:scout {--generate-report}';
    protected $description = 'Generate weekly bounty scout report';

    public function handle(BountyScout $scout)
    {
        $this->info('Generating bounty scout report...');

        $rankedIssues = $scout->rankIssues();
        $assignedIssue = $scout->assignBounty();

        $this->outputReport($rankedIssues, $assignedIssue);
    }

    protected function outputReport(array $rankedIssues, ?Issue $assignedIssue)
    {
        $this->table(
            ['#', 'Score', 'Amount', 'Comments'],
            array_map(function ($issue, $index) {
                return [
                    $index + 1,
                    $issue['score'],
                    $issue['amount'] ?? 'n/a',
                    $issue['comments'],
                ];
            }, $rankedIssues, array_keys($rankedIssues))
        );

        if ($assignedIssue) {
            $this->info("\
Assigned bounty to issue #{$assignedIssue->number}");
        }
    }
}