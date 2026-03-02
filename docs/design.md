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
- The UI should not specify a way to modify configuration files for the test harness. Where appropriate parameters for web UI should be handled without modifying configuration files through the UI. 
  
## Proposed Architecture
To accomplish these goals, the following architecture is proposed:

### Page 1: Landing / Dashboard + Run Test
The goal of this page is to provide a quick, high-level overview of the system to the user with some CTA to promote engagement with the features of the platform.
#### Components:
**Run Tests Button**: A button in the primary accent color of the platform for a user to click, which triggers the running of jobs through the test harness. The UI should call 
In the future, it is possible that the scope of this page contains solver authoring by the user. Thus, it may make sense to leave white space at the bottom of this page for that. In addition, when "run tests" is at the bottom, the click action upon it should take the user to the next page where the results are shown 

### Page 2: Run Jobs
This page details how to select and run a handful of jobs at once 
#### Components:

**Description:** Provide 2-3 sentences of text detailing what a job vs a test is and how the user can identify what is best for them

**Run Jobs:** Offer a select box to choose the tests then allow user to run them all or selected ones with a click, showcase the results on the bottom of the run. This should probably then trigger a POST request to the API backend which serves as a simple wrapper to the CLI, running the selected input tests. If user clicks on results, it will take them to page 3 to explore in further detail the results given. 

**Dry Running:** A user should be able to dry run jobs, checking whether input configurations will work, parsing metrics vs an example output if available, and checking the syntax of the run script (this last one might be overkill). 

**Run Tests:** Offer the run tests button from before as a separate option as well given what the user wants to achieve

**Live Monitoring:** Show the progress bar on jobs that have been completed that fills as the test progresses. Under the test title, it shows the solver, system, resources, and job for that test. The progress bar also shows a percentage of job complete. This is a good example of what I mean, but I want to remove the "remaining" portion of this 
![image](https://github.berkeley.edu/Chem-283/DOW-1-26/assets/3735/78c879e6-21a2-4b47-9c7f-4da5a0beaa6b)


### Page 3: Individual Test Performance
This page details how the most recent test has performed. 
#### Components:
**The Graphs Brent Made Alr for Metrics per Individual Test:** This graph allows a drop down menu to select your job, and then you can see the runtime plotted. Improvements to this include being able to choose from a multiple-choice side panel to minimize the number of clicks, since users can choose multiple things to see per run.

### Page 4: Long-Term Trend Performance
This page details the performance of the system, averaging across multiple tests. Results from individual tests is not within the scope of this page, and they can be included on another page for better user flow. The Long-Term trends view shows a default date range of its components, with an input for the user to set a different desired date range. This date range parameter should use streamlit's session state or other state management tool to keep this date range filter when the user clicks between tabs.  

#### Components:
**Pass/Fail Boxes:** Two boxes of the same size, one detailing the number of passed cases and one detailng the number of failed cases in a given time period. Defaults to descending by date with a drop down input to create a date range for pass/fail. In the bottom of the box is a trend showing the percentage change from the last time period, providing a quick insight into system health

**Test Results Trend Visualization:** A bar chart with passed, failed, and skipped counted. X axis is time, Y axis is count

**Performance Drift Analysis:** An interactive plot that details the performance drift. Not sure how exactly we want to calculate it, but the performance drift visualization allows the user to select, from a toggle-menu, which metric they would like to analyze (GFLOPS, Bandwidth, Throughput, Latency) and for which time period (in days). This supports hover-over interaction to provide more information on each data point, which includes the date and the calculation of the performance drift. The x axis is date and the y-axis is drift (in a percent?). There are also two levels specified to be a warning level, above which the line color changes (to yellow), and an alert level, above which the color changes again (to red). 

**Heatmap:** Used in an example given by William for TACC's test harness, gives more granular information about the test results or performance of a run, say eight different metrics across eight dates. These are shown directly under the performance drift analysis plot and display all defined metrics across the filtered time period.
![image](https://github.berkeley.edu/Chem-283/DOW-1-26/assets/3736/4f8a5252-1cac-45af-9981-3c5be5f60112) (From Texas Advanced Computing Center: High Performance Computing Test
Harness with Jenkins 2017 presentation)

### Page 5: Configuration
This page shows settings that the user can toggle, or this could be a spot to upload configurations as well, given the needs! (Shawn: we may consider just splitting the settings for our application with another page for uploading or managing runner configurations, or just call this page "settings" and don't allow the uploading of configurations through the web UI at all. I'd lean towards the latter but it's fine either way)

## Design System

The UI should have a clear, consistent and appealing visual theme and design language. Streamlit has its own configuration file that includes the ability to configure the theme (see https://docs.streamlit.io/develop/concepts/configuration/theming#working-with-theme-configuration-during-development and https://docs.streamlit.io/develop/api-reference/configuration/config.toml#theme) which should be the preferred method of modifying the visual theme of the UI. Note, it is also possible to fully customize the visual look of any component in streamlit, which can be done by loading a .css file with custom styling for a streamlit component. If a particular styling is desired outside of what is easy to configure using streamlit, note that you can use this method: https://medium.com/pythoneers/how-to-customize-css-in-streamlit-a-step-by-step-guide-761375318e05. 

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

Where necessary, backend communication will be facilitated via REST API requests using python requests or another http server library called via the UI. POST requests are exposed in the backend api where query parameters exceed 2-3 simple parameters or where a data structure such as a list or object dictionary is appropriate as a query parameter. The streamlit frontend will avoid calling the command line interface directly or calling backend functions directly to maintain abstraction between the frontend and backend as well as to utilize the existing asynchronous request available through FastAPI running on a ASGI server. 


