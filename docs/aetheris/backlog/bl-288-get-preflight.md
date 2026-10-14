# BL-288 — Allow GET on the playground preflight (design brief)

**Status:** T0 filed (this document). T1 not started.
**Type:** design brief. A contract for the implementation cc:prompt,
cited by item number.
**Date:** 2026-10-06
**Row:** BL-288 (open, `docs/backlog-2026-06.md` §Harness).
**Evidence:** `docs/evidence/BL-288.md`.
**Citations:** `H` = harness `aetheris` at `91d6a85`; `A` =
`aetheris-agents` at `c733910`.
**Docs-first:** this brief is T0; T1 is a harness-repo commit. **No new
route is named or added** — the read routes already exist (§3.4@H, the
two streams) or are BL-287's T1; this capability is one method on one
list.

---

## 1. Scope

The capability BL-288 files: **a browser can GET a playground route from
an allowed origin.** BL-286's preflight short-circuit answers
`OPTIONS`/`POST` correctly; the allow-methods list (`@allowed_methods
["POST", "DELETE"]`, `cors_plug.ex:47@H`) refuses `GET`, and a browser
GET carrying `Authorization` — every bearer-gated read route — is a
non-simple request the browser preflights. The fix is: GET joins the
list. Nothing else moves.

## 2. Tranches

### T0 — this document (filed)

The row, the evidence file, and this brief, each citing the others. No
code, no harness edit, no route.

### T1 — the implementation ticket (harness commit)

- T1.1 `"GET"` joins `@allowed_methods` (`cors_plug.ex:47@H`) and the
  contract text (C7) is amended in the same commit to match.
- T1.2 Tests: the done-when's two arms — an allowed-origin preflight
  requesting GET returns `204` with `access-control-allow-methods`
  containing `GET`; a real GET with no bearer returns `401`.

## 3. Contract

**C1 — OPTIONS from an allowed origin requesting GET returns 204 before
auth, and Allow-Methods includes GET.** Same mechanism as BL-286's
short-circuit (`cors_plug.ex`, ahead of `AuthPlug`): detection, origin
verdict, then the method decision — `GET` now passes the method check
the way `POST` and `DELETE` already do. The 204 carries the same
`Access-Control-Allow-Headers`, `Access-Control-Max-Age`, and
`Vary: Origin` headers as today; only the methods list grows.

**C2 — a GET with no bearer is still 401.** Auth is not weakened. The
BL-286 settlement carries over verbatim: the preflight is
unauthenticated because browser rules make it so, not because the route
became public; every real GET still runs `AuthPlug` and needs the
bearer. Existing GET routes (§3.4@H, the streams) keep their exact
current behaviour for non-browser and browser callers alike — this
capability changes reachability, not authorization.

**C3 — POST and DELETE stay allowed. No new origin. No new header.**
The origin allowlist (`:api_cors_origins`, default
`["http://localhost:4200"]`, exact match), the allowed-headers list
(five names, `cache-control` included by BL-286's follow-up), and
`Max-Age`/`Vary` are untouched. One element is added to one list.

**C4 — `playground-api.md` is amended by the implementation ticket, not
here.** The CORS preflight block (:863-889@H) gains GET where it names
"POST, DELETE — the playground namespace's mutating methods"; the
wording should name GET with its reason (browser callers read run
status, streams, and BL-287's lists over GET, and every one carries the
bearer), not just append the method. The capabilities appendix gets the
same sentence if T1 touches it, per the BL-287 C7 rule.

## 4. Scout facts relied on

- F1 `@allowed_methods ["POST", "DELETE"]` — `cors_plug.ex:47@H`; the
  header is built from it (`:95@H`).
- F2 The contract names the same two methods — `playground-api.md`
  CORS preflight block, "Allow methods: POST, DELETE"@H.
- F3 The short-circuit exists and is origin-gated ahead of auth —
  `playground-api.md:863-871@H` (BL-286, closed 2026-10-06).
- F4 "Allow headers" excludes nothing relevant: `authorization` is
  already in the header list (`cors_plug.ex:46@H`) — the hole is the
  method, not the header. A GET with `Authorization` fails only on the
  methods arm.
- F5 The blocked surface: `GET /api/playground/runs/:run_id`
  (§3.4@H); both event streams (§3.5/§3.6@H — browser clients read with
  `fetch` because they carry `Authorization`, which makes them
  non-simple); BL-287's two planned GET routes (its C6, open).
- F6 The non-simple test: a request carrying `Authorization` (a
  non-safelisted header) requires a preflight regardless of method —
  so a bearerless GET still preflights *only* when something forces it
  (the spec: GET without safelisted-violating content is simple and
  preflight-free; the bearer makes it non-simple).

## 5. Open for plan STOPs

- The contract wording for GET's reason (this brief proposes the shape
  of the sentence; T1 writes it).
- Whether the capabilities appendix is touched in T1 or filed as a
  separate docs row (BL-287 C7's pattern applies either way).
