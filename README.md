# project-a: Bounty Scout

Agen mingguan yang mencari **open-source bounty berbayar** (≥ US$10) di GitHub yang
cocok dengan keahlian AI/ML, Computer Vision, GIS, IoT, dan Python, lalu
menerbitkan laporan berperingkat sebagai *issue* setiap Senin pagi.

Strategi pendapatan dari riset (produk digital, jasa metodologi, kompetisi)
ada di [docs/INCOME_PLAYBOOK.md](docs/INCOME_PLAYBOOK.md).

# Bounty Scout — week of 2026-10-26
Target: at least US$10/week. One merged bounty of US$50 covers ~5 weeks.

| # | Score | Amount | Stars | Comments | Repository | Issue |
|---|------:|-------:|------:|---------:|------------|-------|
| – | – | – | – | – | – | No bounty passed the filters this week |

## Filtered out
- no stated amount: 79
- bounty-farm repository: 57
- outside expertise: 39
- below minimum amount: 14
- not an organisation repo: 9
- fewer than 500 stars: 2

## Before claiming
- Read the repo's CONTRIBUTING and bounty rules; many ban low-effort or unreviewed AI-generated PRs.
- Check nobody is already assigned or has an open PR (comment count is a proxy only).
- Prefer 💎 Algora bounties: the payout is escrowed by the platform.
- Comment to claim (e.g. `/attempt` on Algora) only when you can deliver within a week.
- Payouts go to your own Algora/IssueHunt/Stripe account; declare the income for tax.

## Cara kerja

1. `.github/workflows/weekly-bounty-scout.yml` berjalan tiap Senin 07:47 WIB
   (atau manual lewat tab *Actions → Run workflow*).
2. `bounty_scout/scout.py` menelusuri issue terbuka tanpa assignee berlabel
   `💎 Bounty` (Algora), `bounty`, dan `issuehunt`.
3. Issue dibuang jika: tanpa nominal, di bawah `--min-amount`, di luar bidang
   (tidak ada kata kunci AI/ML/CV/GIS/IoT/Python), bukan repositori milik
   organisasi, bintang < `--min-stars` (default 500), atau nama repositorinya
   mengandung "bounty" (indikasi *bounty farm*).
4. Sisanya diberi skor: kecocokan bidang, nilai bounty, bonus label Algora
   (dana di-*escrow* platform), tingkat persaingan, dan kebaruan.
5. 20 teratas beserta ringkasan alasan penyaringan diterbitkan sebagai issue
   berlabel `bounty-scout`.

## Menjalankan lokal