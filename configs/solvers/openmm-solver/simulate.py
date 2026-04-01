#!/usr/bin/env python3
"""OpenMM molecular dynamics solver.

Environment variables (set via system config):
  INPUT_PDB   Path to PDB file. Default: inputs/alanine_dipeptide.pdb
  N_STEPS     Number of MD steps. Default: 2000
  SOLVATE     Add explicit TIP3P water box. Default: false
              Set to 'true' for production runs (e.g. WD40 on Slurm).
"""
import os
import sys
import time

from openmm.app import (
    ForceField,
    Modeller,
    NoCutoff,
    PME,
    PDBFile,
    Simulation,
)
from openmm import LangevinMiddleIntegrator
from openmm.unit import (
    kelvin,
    kilojoule_per_mole,
    nanometer,
    picosecond,
    picoseconds,
)

input_pdb = os.environ.get("INPUT_PDB", "inputs/alanine_dipeptide.pdb")
n_steps = int(os.environ.get("N_STEPS", "2000"))
solvate = os.environ.get("SOLVATE", "false").lower() == "true"
timestep_ps = 0.002  # 2 fs

print(f"OpenMM solver starting")
print(f"  PDB:     {input_pdb}")
print(f"  Steps:   {n_steps}")
print(f"  Solvate: {solvate}")

pdb = PDBFile(input_pdb)

ff_files = ["amber14-all.xml"]
if solvate:
    ff_files.append("amber14/tip3pfb.xml")
forcefield = ForceField(*ff_files)

modeller = Modeller(pdb.topology, pdb.positions)
modeller.addHydrogens(forcefield)

if solvate:
    modeller.addSolvent(forcefield, model="tip3p", padding=1.0 * nanometer)

n_atoms = modeller.topology.getNumAtoms()
print(f"  Atoms:   {n_atoms}")

if solvate:
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=PME,
        nonbondedCutoff=1.0 * nanometer,
        constraints=None,
    )
else:
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=NoCutoff,
    )

integrator = LangevinMiddleIntegrator(300 * kelvin, 1 / picosecond, timestep_ps * picoseconds)
simulation = Simulation(modeller.topology, system, integrator)
simulation.context.setPositions(modeller.positions)

print("Minimizing energy...")
simulation.minimizeEnergy()

print(f"Running {n_steps} steps...")
t0 = time.time()
simulation.step(n_steps)
t1 = time.time()

runtime_seconds = t1 - t0
simulation_ns = n_steps * timestep_ps / 1000.0  # ps -> ns
ns_per_day = simulation_ns / (runtime_seconds / 86400.0) if runtime_seconds > 0 else 0.0

state = simulation.context.getState(getEnergy=True)
potential_energy = state.getPotentialEnergy().value_in_unit(kilojoule_per_mole)

print()
print("--- Results ---")
print(f"ns/day: {ns_per_day:.2f}")
print(f"runtime_seconds: {runtime_seconds:.2f}")
print(f"potential_energy_kj_mol: {potential_energy:.2f}")
print(f"n_atoms: {n_atoms}")
print(f"status: success")

sys.exit(0)
