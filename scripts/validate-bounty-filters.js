const axios = require('axios');
const { Octokit } = require('@octokit/rest');

const MIN_BOUNTY_AMOUNT = 10;
const MIN_STARS = 500;
const EXCLUDED_REPOS = ['bounty-farm', 'bounty-hunter', 'bountyboard'];

async function fetchBountyData(issueUrl) {
  const response = await axios.get(issueUrl);
  return response.data;
}

async function fetchRepoDetails(org, repo) {
  const octokit = new Octokit();
  try {
    const { data } = await octokit.rest.repos.get({
      owner: org,
      repo,
    });
    return data;
  } catch (error) {
    console.error(`Failed to fetch repo ${org}/${repo}:`, error.message);
    return null;
  }
}

async function validateBounty(bounty) {
  const errors = [];

  // Amount check
  if (bounty.amount < MIN_BOUNTY_AMOUNT) {
    errors.push(`Amount ${bounty.amount} below minimum ${MIN_BOUNTY_AMOUNT}`);
  }

  // Stars check
  if (bounty.stars < MIN_STARS) {
    errors.push(`Stars ${bounty.stars} below minimum ${MIN_STARS}`);
  }

  // Org repo check
  if (!bounty.isOrganizationRepo) {
    errors.push('Not an organization repository');
  }

  // Excluded repos check
  if (EXCLUDED_REPOS.includes(bounty.repository.toLowerCase())) {
    errors.push('Excluded bounty-farm repository');
  }

  // Outside expertise check
  if (bounty.expertise && !bounty.expertise.includes(bounty.user)) {
    errors.push('Outside expertise requirement');
  }

  return { valid: errors.length === 0, errors };
}

async function processBounties(bounties) {
  const results = [];
  for (const bounty of bounties) {
    const repoDetails = await fetchRepoDetails(bounty.org, bounty.repository);
    const validated = await validateBounty({
      ...bounty,
      stars: repoDetails?.stargazers_count || 0,
      isOrganizationRepo: repoDetails?.organization !== undefined,
    });
    results.push({ ...bounty, ...validated });
  }
  return results;
}

module.exports = { processBounties };
