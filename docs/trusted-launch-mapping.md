# Trusted Launch + Security Benchmarks → Robot Fleet Mapping

This is the conceptual bridge between my current Microsoft Edge Security
work (Gen2 VM Trusted Launch on Azure Local plus the Security Benchmarks
program I own for public and regulated cloud environments) and the
security responsibilities of the Microsoft Robotics platform.

| Edge / Cloud (today)                              | Robot fleet (this repo)                          | Why it matters |
|---------------------------------------------------|--------------------------------------------------|----------------|
| vTPM measured boot (PCR0..7)                      | Robot agent reports simulated PCR digest         | Boot-time integrity is the foundation under everything else |
| UEFI Secure Boot signature chain                  | `firmware_hash` allow-list in `quote.py`         | Stops unsigned firmware from joining the fleet |
| Microsoft Azure Attestation (MAA)                 | `AttestationService` + `FleetCA`                 | Independent third party validates the platform state |
| AAD-issued attestation token                      | Short-lived EdDSA-signed JWT, 5-min TTL          | Credentials must be short-lived and revocable |
| Conditional Access policy on workload identity    | `caps` claim + JWT check before `/cmd_vel` accept | Authorization is a separate gate from authentication |
| Azure Policy `DeployIfNotExists` Guest Config     | Safety envelope policy YAML                      | Compliance is enforced in the control plane, not at the device |
| Regulated cloud network isolation (air-gapped)    | Workspace polygon constraint                     | Physical isolation analogue of network isolation |
| Confidential Computing memory isolation           | Runtime safety envelope on autonomous behavior   | Bounds what the workload can do at the *behavior* level |
| ICM / Sev1 incident response                      | `/safety/intervention` event topic + audit log   | Physical incidents need the same telemetry pipeline as cyber ones |
| Security Benchmarks (CIS-aligned) across the public + regulated fleet | STPA-derived safety envelope on each robot | Declarative policy enforced at the device is the same idea, whether the device is a VM or a robot |

## What carries over directly

- **Mental model of an attested control plane.** I already think in
  terms of "platform measures itself → independent service signs →
  short-lived credential → policy gate on every privileged action."
  That model is exactly what a robot fleet needs.
- **Security baseline ownership at fleet scale.** The Security Benchmarks
  program I run produces distro-agnostic, CIS-aligned baselines that
  enforce a known-good configuration across every Linux device in our
  public and regulated environments. The safety envelope in this repo is
  literally the same shape: declarative policy applied uniformly to every
  device, evaluated continuously, with a clear pass/fail signal.
- **Regulated / air-gapped deployment muscle.** Azure Local ships into
  FFX, AGC, and disconnected environments - robotics deployments
  (manufacturing, defense, healthcare) have the same shape of constraints.
- **Release-gate validation discipline.** The gate I run for TVM is the
  same pattern needed for releasing safety-monitor code: explicit
  criteria, evidence collected, defect escape minimized.

## What I'd be learning on the job

- ROS2 internals beyond the wrapper code in this repo.
- Functional-safety standards work (IEC 61508, ISO 13482, ISO 10218) at
  certification depth rather than literature-review depth.
- Real motion-planning and control-systems intuition.
- Live red-teaming of LLM-driven physical agents at scale - the toy
  scenarios here are the start of an evaluation harness, not the end.
