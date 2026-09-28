<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Issue extends Model
{
    use HasFactory;

    protected $fillable = [
        'number',
        'title',
        'body',
        'bounty_score',
        'bounty_amount',
        'bounty_assigned',
        'comments',
    ];

    protected $casts = [
        'bounty_score' => 'float',
        'bounty_amount' => 'integer',
        'bounty_assigned' => 'boolean',
    ];
}