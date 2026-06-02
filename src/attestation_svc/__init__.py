"""attestation_svc - fake-TPM-quote → JWT identity for simulated robots.

This is the robotics analogue of the Gen2 VM Trusted Launch flow we ship
on Azure today (Azure Local / ALDO):

    Cloud (Gen2 VM)                     Robot fleet (this service)
    ───────────────                     ──────────────────────────
    vTPM measures PCR0..7        ───►   robot agent reports sim-PCR
    Microsoft Azure Attestation  ───►   FleetCA verifies + signs
    AAD-issued attestation token ───►   short-lived JWT for the device
    Policy gates VM workload     ───►   policy gates robot /cmd_vel auth

See docs/trusted-launch-mapping.md for the full mapping.
"""
from .ca import FleetCA
from .quote import RobotQuote, verify_quote
from .service import AttestationService

__all__ = ["FleetCA", "RobotQuote", "verify_quote", "AttestationService"]
