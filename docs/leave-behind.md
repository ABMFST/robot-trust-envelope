# Robot Trust Envelope - one-page leave-behind

**Built by Amir Bredy · TPM II, Microsoft Azure Edge Security**
*For the Microsoft Robotics - Robot Security & Safety opening (200038208)*

---

## The pitch in one paragraph

The cyber control plane a Microsoft Robotics fleet needs looks a lot like
the one I already run on Azure: a hardware root of trust on each device,
an independent attestation service that signs short-lived identity, and
policy (security baselines) that gates every privileged action. I own
both halves of that today on Azure Local: Trusted Launch (vTPM + Secure
Boot) and the Security Benchmarks program for our public + regulated
cloud environments. The two pieces the cloud doesn't have to think about,
**runtime safety envelopes on autonomous behavior** and **adversarial AI
red-teaming of physical systems**, sit naturally on top of that same
substrate. This weekend I built a working prototype that demonstrates the
whole stack end-to-end against a TurtleBot4 sim: attestation, an
STPA-derived envelope that overrides `/cmd_vel` (the per-device analog of
a CIS baseline rule), and an LLM-driven operator that tries to violate
the envelope. The envelope blocks every adversarial scenario.

## What's there
- **Live dashboard + scenario replay:** https://gray-sand-0b848070f.7.azurestaticapps.net
- **Code (public, MIT licensed):** https://github.com/ABMFST/robot-trust-envelope
- **STPA worksheet, architecture diagram, Trusted Launch → robot mapping** in `docs/`.
- **10 unit tests, ruff-clean, CI passing.**

## Why me

| Edge / Cloud (today)                             | Robot fleet (this prototype)                 |
|--------------------------------------------------|----------------------------------------------|
| vTPM measured boot + Secure Boot for Gen2 VMs    | Simulated PCR digest + signed-firmware list  |
| Microsoft Azure Attestation → AAD-issued token   | `FleetCA` issuing short-lived EdDSA JWTs     |
| CIS-aligned Security Benchmarks (public + regulated) | STPA-derived envelope constraints per robot |
| Azure Policy / Guest Configuration               | Envelope policy YAML + override topic        |
| Regulated / air-gapped Azure Local rollout       | Workspace polygon + standoff distance        |
| Release-gate validation pre-launch               | CI + scenario suite gating envelope changes  |

## Honest framing

This is a weekend prototype, not a safety-certified system. The STPA
worksheet is a learning exercise on a toy system; functional-safety
standards expertise is what I'd be growing into on the job. The
engineering quality of the code and the depth of the cloud-to-robot
mapping are the parts I want judged.

**Reach me:** amirbredy@microsoft.com · LinkedIn /in/amirbredy
