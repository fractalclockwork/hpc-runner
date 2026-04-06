# UI Design 
Authors: Shree Patel and Shawn Schulz
Last Updated: 3 March 2026

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
- The UI should not specify a way to modify configuration files for the test harness. Where appropriate parameters for web UI should be handled without modifying configuration files through the UI. 
  
## Proposed Architecture
To accomplish these goals, the following architecture is proposed:

### Page 1: Landing / Dashboard + Run Test
The goal of this page is to provide a quick, high-level overview of the system to the user.
#### Components:
**System Description**: A few paragraphs explaining the premise of the solver and the system.

### Page 2: Run Solvers
This page details how to select and run a handful of solvers at once or individually
#### Components:

**Description:** Provide 2-3 sentences of text detailing what a solver is and how the user can identify what is best for them

**Solver Overview**: A drop-down box containing a table of available solvers

**Run a Batch**: The user can choose solvers to run as a batch from checkbox selection, and those can then be run from that place in the UI.

**Active Runs/Live Monitoring:** Show the progress bar on jobs that have been completed that fills as the test progresses. Under the test title, it shows the solver, system, resources, and job for that test. The progress bar gives an indicator to the user that their solver is still in progress. This is also one spot where the user can stop an asynchronous job

**Run Solvers (Individually):** Offer a set of tabs, one for each solver, to choose the solver then allow user to run it with a click or pull up the last run. Each solver gets an invocation ID and the results are shown at the bottom of the run. These jobs are technically run asynchronously and can also be cancelled from this portion too.  

### Page 3: Run History
This page details the runs that have been completed thus far one by one
#### Components: 

**History Dropdown**: In this region, the user can click on each run as a drop-down to see the stdout, metrics, and stderr of each run. This can be filtered, grouped, and manipulated to showcase the runs that are useful. Check-mark and "X" emojis denote whether the run succeeded or failed. 

### Page 4: Individual Test Performance
This page details how the most recent test has performed. 
#### Components:
**Grasphs of Individual Test Metric performance:** This graph allows a drop down menu to select your job, and then you can see the runtime plotted. Improvements to this include being able to choose from a multiple-choice side panel to minimize the number of clicks, since users can choose multiple things to see per run.

### Page 5: Long-Term Trend Performance
This page details the performance of the system, averaging across multiple tests. Results from individual tests is not within the scope of this page, and they can be included on another page for better user flow. The Long-Term trends view shows a default date range of its components, with an input for the user to set a different desired date range. This date range parameter should use streamlit's session state or other state management tool to keep this date range filter when the user clicks between tabs.  

#### Components:
**Pass/Fail Boxes:** Two boxes of the same size, one detailing the number of passed cases and one detailng the number of failed cases in a given time period. Defaults to descending by date with a drop down input to create a date range for pass/fail. In the bottom of the box is a trend showing the percentage change from the last time period, providing a quick insight into system health

**Test Results Trend Visualization:** A bar chart with passed, failed, and skipped counted. X axis is time, Y axis is count

**Performance Drift Analysis:** An interactive plot that details the performance drift. Not sure how exactly we want to calculate it, but the performance drift visualization allows the user to select, from a toggle-menu, which metric they would like to analyze (GFLOPS, Bandwidth, Throughput, Latency) and for which time period (in days). This supports hover-over interaction to provide more information on each data point, which includes the date and the calculation of the performance drift. The x axis is date and the y-axis is drift (in a percent?). There are also two levels specified to be a warning level, above which the line color changes (to yellow), and an alert level, above which the color changes again (to red). 

**Heatmap:** Used in an example given by William for TACC's test harness, gives more granular information about the test results or performance of a run, say eight different metrics across eight dates. These are shown directly under the performance drift analysis plot and display all defined metrics across the filtered time period for a solver. Another possible component could allow the comparison of different solvers for shared metrics for a selected time period, i.e. the runtime performance of Gaussian vs Q-Chem vs ACES for the past 15 runs that included all 3 solvers. Another component could handle system solver combinations etc. They provide a 2 dimensional comparison of solver, system or hardware combinations for different time points for a particular shared metric. Ideally provide easy way for user to plugin their own heatmaps to examine different combinations of data.
![image](https://github.berkeley.edu/Chem-283/DOW-1-26/assets/3736/4f8a5252-1cac-45af-9981-3c5be5f60112) (From Texas Advanced Computing Center: High Performance Computing Test
Harness with Jenkins 2017 presentation)

### Page 6: Configs
This page shows the configs available to the user on the back-end. They cannot be edited from this page, simply viewed. 

## System Design Principles
Fonts: Streamlit basic font is fine imo

Forms: For buttons, I think they should be in a different blue color for user attention.

Colors: I think a blue scheme would complement black or white well, and signals proficiency, innovation, and steamlined-ness for the user. See these two color suggestions:
![image](https://github.berkeley.edu/Chem-283/DOW-1-26/assets/3735/48601f78-bfc4-446c-a9bf-a9204b776163)

If not these, then we can go with Dow red, or some other accent color (not purple, not pink, not orange, not yellow, and not a pastel).

Icons: I don't think being an emoji-heavy platform is professional, but we can use gears and other icons for the sidebar for better user interactivity. Agree regarding avoiding emojis. Perhaps we could consult with Dow/capstone mentors about this topic, there are lots of good open source icon libraries we could use in addition to the free templates on figma and other platforms (see https://iconoir.com/ which has figma integration as one possibility). 

## State Management

The UI should maintain the minimum state possible to meet user experience requirements. To this end, a few aspects of the UI state need to be tracked, such as date filters, any performance metric filters and other manipulations of the UI a user makes. Streamlit provides an idiomatic method to save/cache some of this information in it's session management component: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state


A few key data should be kept in a streamlit session state, namely: the date range for the test results page, the date range for long term trend visualization, the tests currently selected to run as a group on the run jobs page, whether to run the selected tests as a dry run or full run. In general though we would like to maintain the minimum possible state necessary to create the required user experience in the UI. 

## Backend Communication

Where necessary, backend communication will be facilitated via REST API requests using python requests or another http server library called via the UI. POST requests are exposed in the backend api where query parameters exceed 2-3 simple parameters or where a data structure such as a list, dictionary, or object is appropriate as a query parameter. The streamlit frontend will avoid calling the command line interface directly or calling backend functions directly to maintain abstraction between the frontend and backend, keep the user's underlying system abstracted from the web browser interface, as well as to utilize the existing asynchronous request available through FastAPI running on a ASGI server. 


