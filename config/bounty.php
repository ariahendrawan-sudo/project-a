<?php

return [
    'api_url' => env('BOUNTY_API_URL', 'https://api.github.com/repos/ariahendrawan-sudo/project-a/issues'),
    'cache_ttl' => env('BOUNTY_CACHE_TTL', 24),
    'min_score' => env('BOUNTY_MIN_SCORE', 5.0),
    'max_bounties' => env('BOUNTY_MAX_PER_WEEK', 5),
];