# UI Design 
Authors: Shree Patel and Shawn Schulz
Last Updated: 28 February 2026
## Objective
This file details the goals, design, and scope of the UI components of this project. 
## Overview
Dow’s HPC environment must undergo frequent security‑driven software and system updates, but the company currently lacks a reliable way to detect when these changes break or degrade scientific software performance. Dow’s small HPC team supports critical R&D workloads in computational chemistry, molecular dynamics, CFD, and AI. They need a lightweight, maintainable system that ensures solver performance remains stable as security requirements force more frequent updates.
Our team will build a modular, execution‑agnostic automated testing platform that runs scientific workloads, detects regressions, and visualizes performance changes over time. Within scope of this deliverable is a functional prototype test harness, a modular configuration system, a performance‑tracking dashboard, documentation, and a public GitHub repository suitable for community maintenance.
## Goals and Non-Goals
### Goals
Overarching goals of the project are to support the business in maintaining reliability of computational chemistry workloads, meeting new corporate security requirements requiring frequent system updates, minimizing downtime and performance regressions, and reducing manual testing burden on a small HPC staff.
Within this set of goals, the UI is critical to ensure that the user can:
- Run tests, schedule jobs, and trigger the execution of the test runner harness from the UI
- Display results of said jobs, including key metrics parsed from the metric extraction and logging layer
- Provide visualizations of current and historical data in a variety of interactive methods to ensure proper exploration of the system. This includes but is not limited to: heatmaps, performance trend tracking, and system health reports
### Non-Goals
- For the current implementation, we do not want to specify a way to author new solvers within the UI interface
## Proposed Architecture
To accomplish these goals, the following architecture is proposed:
