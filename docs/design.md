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
### Page 1: Landing / Dashboard + Run Test
The goal of this page is to provide a quick, high-level overview of the system to the user. 
#### Components:
**Pass/Fail Boxes:** Two boxes of the same size, one detailing the number of passed cases and one detailng the number of failed cases in a [BLANK] time period (@Shawn, should this be something the user can configure?). In the bottom of the box is a trend showing the percentage change from the last time period, providing a quick insight into system health
**Run Tests Button**: A button in the primary accent color of the platform for a user to click, which triggers the running of jobs through the test harness. (NOTE TO SELF: PROVIDE DOCUMENTATION ON WHAT IS CALLED IN THE BACKEND)
In the future, it is possible that the scope of this page contains solver authoring by the user. Thus, it may make sense to leave white space at the bottom of this page for that. In addition, when "run tests" is at the bottom, the click action upon it should take the user to the next page where the results are shown 
### Page #: Individual Test Performance
This page details how the most recent test has performed. 
#### Components:


### Page #: Performance
This page details the performance of the system, averaging across multiple tests. Results from individual tests is not within the scope of this page, and they can be included on another page for better user flow. 
#### Components:
**Test Results Trend Visualization:** A bar chart with passed, failed, and skipped counted. X axis is time, Y axis is count
**Performance Drift Analysis:** An interactive plot that details the performance drift. Not sure how exactly we want to calculate it, but the performance drift visualization allows the user to select, from a toggle-menu, which metric they would like to analyze (GFLOPS, Bandwidth, Throughput, Latency) and for which time period (in days). This supports hover-over interaction to provide more information on each data point, which includes the date and the calculation of the performance drift. The x axis is date and the y-axis is drift (in a percent?). There are also two levels specified to be a warning level, above which the line color changes (to yellow), and an alert level, above which the color changes again (to red). 
