# Proxy network course content review

Course: `proxy-network-judgment-lab-20260920`.

## Teaching review

The combined source material is reorganized into 32 independent judgment units in six modules. Every unit declares prerequisite units, object meanings and ownership, a complete worked example, one changed condition, unchanged conditions, a prediction, a separate hint and answer, one possible confusion, a minimal repair, and the limits of verification. All examples are anonymized teaching settings; commercial prices, response times and session guarantees are explicitly hypothetical. No learner answers or private account records are published.

The glossary remains a lookup index rather than a required vocabulary dump. Classification by subject is kept separate from learning dependencies. The complete web course is publication mode under math-cs-concept-tutor; it does not claim to perform a live wait-and-assess conversation. Reading, self-assessment and independent demonstrated ability remain distinct.

## Technical corrections

- Explicit application proxies and TUN interception are separate paths; target DNS may occur remotely or be satisfied by cache.
- OS longest-prefix selection and ordered proxy-rule matching are different algorithms.
- Global mode applies after traffic reaches the core; en0 is a physical carrier, not a DIRECT policy proof.
- A 198.18 address can appear as a synthetic mapping or a local next hop; the field's role matters. It is not a public exit or evidence of a particular application.
- ICMP is not a mandatory stage between DNS and TCP. HTTP/3 uses QUIC rather than the traditional TCP path.
- MTU/PMTUD is a hypothesis requiring evidence, not an automatic diagnosis from TLS timeouts.
- Registration, routing origin, physical deployment, database location, product labels and reputation are separate evidence dimensions.
- Different risk scores are not interchangeable measurements or guarantees about a service's private decisions.
- Test traffic, real traffic, TTFB, effective first token, failures and connection reuse use separate measurement definitions.

Definitions are grounded in primary protocol, implementation and provider-database documentation listed in the course. Listing a provider classification does not establish a target service's internal risk policy.

## Release evidence boundary

This file records content review, not execution results. Source identity and structural checks are produced by the build and gate commands. Actual browser checks are produced by `tools/check-microcourses.py --built-site ...`; workflow artifacts preserve the tested HTML, screenshots and report. A green workflow does not demonstrate learner mastery. Chromium print-media checks do not imply paginated-PDF or Safari/WebKit validation. Public deployment and readback must be confirmed separately for the published commit.
