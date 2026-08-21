"""Workflows for Optical Coherent Pluggable subscriptions.

The module ships the ready-to-use ``create_optical_coherent_pluggable`` /
``modify_optical_coherent_pluggable`` / ``terminate_optical_coherent_pluggable`` /
``validate_optical_coherent_pluggable`` workflows for the shipped product
type, together with the importable parts (form generators and block-level
steps exported as ``StepList`` constants). Consumers with their own product
type compose their own ``@create_workflow`` / ``@modify_workflow`` /
``@terminate_workflow`` / ``@validate_workflow`` with these parts and their own
construct/store steps; the shipped block steps bind to
``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY`` (see
:mod:`orchestrator.optical.workflows.optical_coherent_pluggable.shared`).
"""
