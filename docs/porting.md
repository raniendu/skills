# Porting skills

Port the reusable expertise, not the original agent's private environment.
Read [the standard](skill-standard.md) before copying any content.

## Provenance and license

Before importing:

1. Record the upstream repository or document URL, exact revision, original author,
   license, and the files being adapted. For private source material, obtain
   explicit permission to publish a sanitized adaptation.
2. Check reuse and redistribution rights. Public availability is not permission;
   no-license and unclear-license material require maintainer clarification.
3. Keep required copyright notices, license text, and attribution within the skill
   directory. Preserve third-party terms; do not simply replace them with MIT.
4. Record provenance in `references/SOURCES.md`, including local modifications,
   the upstream revision, and how future upstream updates should be reviewed.
   Explain any separately licensed assets or code and their scope.
5. If the original material is your own, state that fact and identify its source
   without exposing private filesystem paths or sensitive repository details.

Provenance documentation is required for ports, not for wholly original skills.
Never fetch and merge upstream instruction changes automatically.

## Porting checklist

- [ ] Identify the task, actual successful workflow, triggers, and non-goals.
- [ ] Establish permission and preserve upstream notices before copying.
- [ ] Inventory bundled scripts, dependency versions, assets, and external calls.
- [ ] Remove credentials, personal data, private endpoints, hostnames, absolute
      home paths, account IDs, and copied production output.
- [ ] Replace incidental tool names with capabilities, preserving any dependency
      that is genuinely essential to the workflow.
- [ ] Replace personal preferences with explicit inputs or documented defaults.
      Keep application policy in its application repository rather than importing
      it into a general skill.
- [ ] Make paths relative to the skill root and define the output path contract.
- [ ] Reassess consent, costs, destructive steps, injection risks, and recovery.
- [ ] Document feature gaps; do not claim portability by deleting safety checks or
      silently changing the model, service, output, or permissions.
- [ ] Set metadata honestly and add compatibility requirements where needed.
- [ ] Add routing, behavior, failure, and safety cases to `TESTING.md`.
- [ ] Test outside the original checkout and record evidence and limitations.
- [ ] Review the final skill as executable guidance, not just as prose.

## Compatibility and installation

There are two independent claims:

- **Format compatibility:** this skill follows the Agent Skills format and this
  repository's stricter profile.
- **Runtime compatibility:** the documented task was actually executed by a named
  agent/runtime version with the stated tools and environment.

Do not infer the second from the first. Record versions, dates, inputs, outcomes,
and gaps in `TESTING.md`. A portable experimental skill can have limited evidence;
a stable portable skill requires successful checks in at least two distinct
agent implementations. A stable agent-specific skill must pass on its declared
agent and remain labeled agent-specific.

Consumers must consult their own agent's current documentation for installation.
Some discover `.agents/skills/`, some support other project/user directories,
and some accept explicit resource paths. A repository clone is not automatically
active in every agent. Do not install to all agents or overwrite existing skills
without an explicit request.

Prefer one canonical skill directory over per-agent copies. If a small optional
agent adapter is essential, keep its instructions under that skill's
`references/`, explain when to read them, and retain a portable core. If the core
cannot work without a specific agent API, label it `agent-specific` and declare
that dependency rather than presenting it as universally compatible.

Review and pin a repository revision before installation. Copy the complete
skill directory, including scripts, resources, test evidence, and license files;
copying `SKILL.md` alone may produce an incomplete or noncompliant installation.

## Upstream changes

Record the source and destination revisions for each update. Compare behavior,
permissions, licenses, dependencies, and output contracts before incorporating
changes. Re-run affected tests. A previous review does not approve a new version.
