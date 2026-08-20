# Design: Web Portal OpenSpec

## Context

As-built: one TypeScript-Node Compose service, port 5173, user `node`, external network, no database.

In-force ADRs: 0001, 0006, 0010.

## Goals / Non-Goals

**Goals:** SoT + Spec Kit parity with other packs.

**Non-goals:** Adding API base URL to Compose; adding a database.

## Decisions

- Mirror Haystack/REST OpenSpec requirement/scenario style.
- Spec Kit 001 includes contracts/compose-env.md for ports/user/network only.

## Risks / Trade-offs

- [Portal app sources live in another volume] → Pack specs describe the container, not the React routes.

## Open Questions

None.
