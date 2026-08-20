# Design Partner Program

PN Labs is looking for a small number of legitimate scraping/web-retrieval workloads to test whether conservative outcome classification improves reliability and efficiency.

## Good fit

A useful workload has one or more of these symptoms:

- adding more proxies made success rate worse;
- repeated 403/429/451 outcomes trigger blind rotation;
- proxy expiry/authentication failures poison a pool;
- response outcomes are mixed with endpoint-health scoring;
- requests-per-usable-result is high or unstable;
- multiple providers expose inconsistent failure semantics.

## What we measure

We prefer A/B evidence over testimonials.

- valid success rate;
- upstream requests per usable result;
- unnecessary rotations;
- observed HTTP/proxy-path outcome mix;
- latency distribution;
- bandwidth or provider cost per usable result, when safely measurable.

## Safe inputs only

Preferred inputs are:

- sanitized aggregate counts;
- synthetic reproducer code;
- redacted outcome summaries;
- non-sensitive configuration shapes with placeholders.

Do **not** send or post:

- production logs, HAR/PCAP captures, or raw request dumps;
- passwords, tokens, API keys, cookies, authorization headers, or proxy credentials;
- credential-bearing proxy URLs;
- private endpoint URLs/IP addresses, internal hostnames, or infrastructure topology;
- private datasets, personal data, or customer data;
- non-public implementation details that you are not authorized to disclose.

If a reproduction depends on sensitive production evidence, reduce it to a synthetic case before sharing.

## What this is not

The program is not an offer to bypass access controls. Tests should use workloads the participant is authorized to run and should respect applicable target policies, rate limits, and law.

## Contact

Open a GitHub issue in this repository with the prefix `[design-partner]` and only the sanitized workload class, aggregate baseline, and metric you want to improve.
