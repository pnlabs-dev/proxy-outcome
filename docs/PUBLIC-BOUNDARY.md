# Public boundary

This repository is intentionally a **small public baseline**, not a source dump of PN Labs commercial systems.

## Included publicly

- deterministic observation classification;
- public outcome/attribution schema;
- conservative evidence flags;
- CLI and examples using synthetic values;
- unit tests and CI;
- public security/hygiene checks;
- documentation required to understand and safely use the library.

## Intentionally excluded

The public repository does not contain:

- commercial routing or control-plane implementation;
- private scoring weights, ranking logic, or optimization heuristics;
- provider selection logic or provider-specific private configuration;
- historical learning state or non-public benchmark datasets;
- production endpoints, IP addresses, credentials, tokens, cookies, or internal hostnames;
- infrastructure topology, deployment secrets, operational runbooks, or private incident data;
- customer/workload data or private design-partner material.

## Contribution rule

Contributions should improve the public deterministic baseline without requiring disclosure of private infrastructure or third-party secrets.

If a proposed change needs sensitive production evidence, reduce it to a synthetic reproducer or sanitized aggregate result before opening an issue or pull request.
