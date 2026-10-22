# StableKite default branch — experimental Python 3.15t gevent

This default-branch state is **EXPERIMENTAL**, intentionally exposed for the project's default-branch pipeline.
It is NOT a full gevent release and NOT an upstream-ready PR. Existing user-accepted source-only and native
candidate was gevent 26.9.0 from commit b17b199a96287d72d13afb0a74743e7f26bbe743. The upstream fork's prior master remains
in the Git parent history at 08f09eda118b6ee050f93fe645711f5d7051c2ed and contains the upstream development-version change to 26.9.1.
The merged default branch therefore reports gevent **26.9.1 developmental version**; this must be
qualified separately from the original 26.9.0 experiment. Do not infer the 26.9.0 runtime pass for this merge
without a new Windows+Linux build and scoped runtime verification. Keep explicit/no-silent-GIL switch checks.

CURRENT LIMITATIONS: current FT monkey.patch_all and native gevent.ares fail closed rather than work.
They MUST be repaired for the user's full functional parity + strict pyright + true no-GIL objective.
Native CFFI short tests are not broad upstream API tests. Upstream PR and production release remain NO-GO.
No third-party full gevent support or GIL-free compatibility claim is implied by default-branch distribution.
Experimental branch stablekite/cp315t-cffi-a271-experimental is deliberately retained for provenance.
