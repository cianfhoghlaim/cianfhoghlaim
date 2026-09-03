# Spec Delta: tuatha-platform

## ADDED Requirements

### Requirement: Pent-Elemental Cosmology + Anam Cara

The `tuatha-mmo` skill SHALL model the in-game cosmology
on the five classical Celtic elements (Spirit, Water,
Fire, Earth, Air) plus the **Anam Cara** mechanic. The
`sruth/tuatha/game/` quadrant module MUST consume the same
cosmology. The cosmology drives:

- The 5 playable classes
- The 5 quest tracks
- The Soul Level progression system
- The Geasa vow system (binding promises with real
  in-game consequences)

#### Scenario: A new quest content pack is added

- **GIVEN** a developer wants to add a "Water" quest pack
  (river spirits + sovereignty)
- **WHEN** they look at `.agents/skills/tuatha-mmo/SKILL.md`
  + the Anam Cara reference at
  `.agents/skills/tuatha-mmo/references/mythology-pent-elemental-cosmology.md`
- **THEN** the developer sees:
  - The 5 elements (Spirit / Water / Fire / Earth / Air)
  - The Anam Cara mechanic (soulbound NFT + binding vow)
  - The 5 quest tracks (one per element)
  - The Geasa system (binding + status)
- **AND** the new quest pack can be added without
  re-deriving the cosmology

### Requirement: x402 + SIWE + Crypteolas Federated Learning

The `tuatha-mmo` skill SHALL wire together the 3 crypto
primitives (x402 payments, SIWE auth, Crypteolas
federated learning) into the MMO economy. The canonical
flow:

1. Player signs in via SIWE (Ethereum wallet) → Pocket ID
   OIDC JWT
2. Player buys in-game item → x402 HTTP 402 paywall
3. Player's model is updated locally (Flower) → federated
   round on Crypteolas infrastructure

The three protocols share the same wallet identity
(sovereign game state in SpacetimeDB, the
`AnamCara-NFT`).

#### Scenario: A player buys a soulbound NFT

- **GIVEN** a player is on the Tuatha MMO dashboard with
  a valid SIWE session
- **AND** the player clicks "Purchase Anam Cara NFT"
- **WHEN** the FastAPI endpoint receives the request
- **THEN** the endpoint returns HTTP 402 with the
  x402-payment-required header
- **AND** the player signs the payment authorization
- **AND** the endpoint mints the Anam Cara NFT (ERC-5114
  SBT) on Solana via Metaplex Core
- **AND** the new NFT is bound to the player's SIWE
  wallet in SpacetimeDB

#### Scenario: A new Crypteolas federated round starts

- **GIVEN** the Crypteolas Flower server has scheduled a
  new training round
- **WHEN** 5+ player clients check in
- **THEN** the server distributes the current model
  weights
- **AND** each client trains locally on its private data
- **AND** the clients return only the gradient updates
  (not the data)
- **AND** the server aggregates the gradients
- **AND** the updated model is signed and stored in
  SpacetimeDB for the next round

## REMOVED Requirements

(None.)
