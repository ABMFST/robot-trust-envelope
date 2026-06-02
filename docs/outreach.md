# Outreach package - Tim

All three artifacts below pitch the same thing in three formats. Pick the
one that fits the channel. The site URL is the lead asset; everything
else is supporting context.

**Site:** https://gray-sand-0b848070f.7.azurestaticapps.net
**Repo:** https://github.com/ABMFST/robot-trust-envelope (public, MIT licensed)

---

## A) Email - short cold send

> Subject: Robot security & safety role - built a prototype that bridges to what I do today
>
> Hi Tim,
>
> I saw the Member of Technical Staff opening on your Microsoft Robotics
> team (Robot Security & Safety, 200038208). I run Trusted Launch (vTPM
> + Secure Boot) for Azure Local and own the Security Benchmarks program
> for public and regulated cloud environments across that fleet. The
> parallels between the edge/cloud control plane I work in and what your team
> is building for robot fleets jumped out at me, so I spent the weekend
> building a working prototype to make that case concretely.
>
> Three components on top of a TurtleBot4 sim: an attestation service
> that mirrors my Trusted Launch flow, a runtime safety envelope derived
> from a (toy) STPA analysis that plays the same role security baselines
> play across the Linux fleet, and an LLM-driven red-team operator that
> tries to drive the robot outside the envelope. Live dashboard, demo
> trace, and architecture write-up here (repo is public, MIT licensed):
>
> https://gray-sand-0b848070f.7.azurestaticapps.net
>
> Could I steal 20 minutes to walk you through it and hear what you'd actually want this team to
> own? Either way, congrats on the charter - the cyber + functional
> safety + AI safety overlap is exactly the kind of seam that's
> historically been hard to staff.
>
> Thanks,
> Amir
> amirbredy@microsoft.com · TPM II, Azure Edge Security

---

## B) LinkedIn DM - even shorter

> Hi Tim - saw the Robot Security & Safety MTS role on your team. I run
> Trusted Launch for Azure Local and own the Security Benchmarks program
> for our public + regulated cloud environments. Those patterns map
> cleanly to a robot fleet, so I spent the weekend prototyping it:
> attestation + an STPA-derived safety envelope (the per-device analog of
> a security baseline) + an LLM red-team that the envelope blocks. Live
> demo + write-up: https://gray-sand-0b848070f.7.azurestaticapps.net
> - would love 20 minutes to walk through it.

---

## C) One-page PDF leave-behind

`leave-behind.md` (also rendered to `leave-behind.pdf` after you run
`python -m scripts.render_pdf`) - single page, three sections:

1. **The pitch in one paragraph.**
2. **The architecture diagram** (`docs/architecture.svg`).
3. **Why me:** three bullets mapping Azure Trusted Launch + Security
   Benchmarks (public + regulated) → Robot Trust Envelope, with the live
   URL + repo URL footer.

---

## Honest framing notes

- Lead with the *bridge* (Trusted Launch + Security Benchmarks → robot
  fleet). Don't open with ROS2 or STPA - those are the stretch, not the
  strength.
- Be explicit that the STPA worksheet is a learning exercise, not a
  certification-grade safety case. Tim will know the difference instantly
  and will respect the honesty.
- "Could I steal 20 minutes" beats "I'd love to interview." You're
  exploring fit, not pre-empting his recruiter process.
