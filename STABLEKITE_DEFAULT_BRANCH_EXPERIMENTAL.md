# A279 experimental CPython 3.15t native gevent; full upstream compatibility remains NO-GO

This DEFAULT-branch Python 3.15t source is deliberately **EXPERIMENTAL** for StableKite's existing default-branch pipeline.
The A279 update fixes scoped free-threaded monkey.patch_all, native Cython c-ares, private libuv loops and fork watcher teardown on Windows.
Actual native Windows CPython 3.15t source wheel: SHA256 326fcad020a604dd285668bf828fecb5b5bbff491aab40a5c230adc76ad1fff3 with scoped real tests 6/6, including GIL normal/off/on,
CFFI libuv, native c-ares, 2 OS threads, Hub.destroy(destroy_loop=True) and monkey-patching. Linux CPython 3.15t source wheel SHA256
27a6dc3a2b6faf66d49952a7120886279f94d4c6bb66ca640626a0017305c87e with CFFI libev/libuv, native c-ares and scoped real GIL off/on tests, including 4 genuine OS threads.
Passing these bounded acceptance cases DOES NOT establish full gevent API parity, strict Pyright (still errors), process-wide
SSL, signal/fork, long-stress or upstream release readiness. Upstream PR and production release are STRICT NO-GO.
Do not silently enable the GIL on free-threaded CPython. This branch remains a development build (26.9.1.dev0).

## Prior experimental default-branch note (A274; historical)

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
