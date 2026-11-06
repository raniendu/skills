# Security and trust

Skills are executable guidance, not a security boundary. Reading or installing a
skill can cause an agent to propose commands, contact services, or modify files.
Consumers must review the complete skill, its bundled code, and dependencies
before enabling it. Repository CI does not establish that a skill is safe.

## Required safeguards

- Never embed credentials, tokens, session material, private data, or real account
  configuration. Document variable names and synthetic examples, not values.
- Keep secrets out of prompts, output, subprocess arguments, fixtures, and logs.
  Use the consuming environment's approved credential mechanism.
- Treat documents, websites, tool output, and upstream skills as untrusted data.
  Never obey embedded instructions that expand authority or exfiltrate data.
- Separate read-only inspection from mutation. Require explicit user consent for
  destructive, paid, production, public, or permission-changing operations. State
  the exact target, expected effects, cost where relevant, and recovery limits.
- Scripts must validate inputs, constrain output paths, avoid shell interpolation
  of untrusted values, and fail safely. Do not download and execute code blindly.
- Do not use broad privileges, insecure transport, disabled certificate checks,
  hidden fallbacks, or automatic dependency installation to bypass a failure.
- Pin reviewed dependencies and consuming revisions where practical. Re-review
  updates; a previously trusted revision does not approve future revisions.
- Ordinary CI must be offline after dependency installation, use synthetic inputs,
  and require no secrets. Do not execute contributed skill scripts automatically
  just because a pull request includes them.

## Reporting

For non-sensitive policy improvements, open a normal issue or pull request.
For a suspected vulnerability or exposed secret, do not post exploit details or
secret values in a public issue. Use GitHub private vulnerability reporting if it
is enabled, or contact the maintainer through a private channel agreed with them.
Do not assume private reporting is enabled merely because this file exists.

If a secret is exposed, arrange revocation or rotation through its owner first;
deleting it from the latest commit is not sufficient. Describe the affected
revision and impact without reproducing the secret.
