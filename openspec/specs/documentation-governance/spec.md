# Documentation Governance Specification

## Purpose

Agreed rules for **OpenSpec**, **OpenSPDD**, and **ADR** in this configuration repository so humans and coding agents share one change workflow.

Change history:

- `openspec/changes/archive/2026-08-20-adopt-openspec-openspdd-adr/`

In-force ADR: `adr/0010-openspec-openspdd-adr-documentation-model.md`.

## Requirements

### Requirement: OpenSpec schema spec-driven-with-adr

Every `openspec/config.yaml` in this repository MUST set `schema: spec-driven-with-adr`. A behavior-changing change MUST produce artifacts in order: proposal → specs → design → adr → tasks.

#### Scenario: Root config declares the schema

- **GIVEN** a checkout of this repository
- **WHEN** `openspec/config.yaml` is read
- **THEN** it contains `schema: spec-driven-with-adr`

### Requirement: Durable ADRs at repo root

Architectural decisions that establish a long-term pattern, technology, boundary, or contract MUST be recorded as `adr/NNNN-kebab-title.md`. Accepted ADR files MUST NOT be edited. A later decision MUST add a new ADR that supersedes the prior file. Change-local `openspec/changes/<id>/adr.md` MUST be a review manifest that references `adr/` files and MUST NOT duplicate full ADR bodies.

#### Scenario: ADR index exists

- **GIVEN** a checkout of this repository
- **WHEN** an operator opens `adr/README.md`
- **THEN** the in-force set is listed with paths to numbered ADR files

#### Scenario: Change manifest does not replace ADRs

- **GIVEN** an OpenSpec change folder
- **WHEN** `adr.md` is present
- **THEN** it lists in-force ADRs reviewed and any new `adr/NNNN-*.md` files created
- **AND** it does not replace the `adr/` folder as the decision log

### Requirement: OpenSPDD REASONS canvases

The repository MUST keep OpenSPDD REASONS Canvas prompts under `spdd/prompt/` for the platform and each pack (Requirements, Entities, Approach, Structure, Operations, Norms, Safeguards). After implementation drift, canvases MUST be updated (equivalent to `/spdd-sync`) in the same change as the code.

#### Scenario: Pack canvases present

- **GIVEN** a checkout of this repository
- **WHEN** `spdd/prompt/` is listed
- **THEN** canvases exist for `platform-devcontainers`, `haystack-devcontainer`, `rest-api-devcontainer`, and `web-portal-devcontainer`

### Requirement: Spec Kit aligned with OpenSpec SoT

Each pack MUST keep GitHub Spec Kit feature packages under `specs/00N-…/` whose requirements and contracts match the pack OpenSpec SoT. Spec Kit is a workbook (stories, verification, contracts), not a competing SoT.

#### Scenario: Web Portal has Spec Kit and OpenSpec

- **GIVEN** a checkout of this repository
- **WHEN** an operator inspects `Heavy-Rental-Web-Portal/`
- **THEN** both `openspec/specs/web-portal-devcontainer/spec.md` and `specs/001-web-portal-devcontainer/` exist

### Requirement: Process document

The repository MUST publish `docs/spec-governance.md` describing the three layers, artifact locations, change order, and pack capability map.

#### Scenario: Governance doc present

- **GIVEN** a checkout of this repository
- **WHEN** `docs/spec-governance.md` is opened
- **THEN** OpenSpec, OpenSPDD, and ADR are defined with paths and a change workflow
