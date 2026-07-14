# ai-platform Transaction Log

Auto-maintained by `mise run commit` (`scripts/git_commit.py` + `tools/transaction-log/`) — appends a delta summary in the same commit as the code change it describes (headline = verbatim commit message). Cleared on **push to main**, not a version bump — this repo has no running artifact to stamp, so push is its genuine "publish" event (see `mise.toml`'s header comment). Full history: `git log -p transaction-log.md`. Read this file at session start for recent context. Do not edit by hand.

<!-- TRANSACTION_LOG_START -->
## Add ai-platform mise.toml: check + commit + gh tasks (no bump/restart)
- scripts/git_commit.py           | 111 ++++++++++++++++++++++++++++++++++++++++
- templates/golden-path/README.md |  16 ++++++
- transaction-log.md              |   6 +++
- 5 files changed, 207 insertions(+)

<!-- TRANSACTION_LOG_END -->
