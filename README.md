# The-L-Analysis
The CTA L Analysis App is a Python-based command-line application designed to analyze the daily ridership of the Chicago Transit Authority (CTA) L train system. The app allows users to query a SQLite database containing ridership data, station information, and other related data to generate various ridership reports, comparisons, and plots.

## Prerequisites

* Python 3.x
* SQLite3 (included in Python standard library)
* matplotlib

## Installation

1. Ensure you have Python 3.x installed on your system.
2. Install the required packages using pip:
```BASH
pip install matplotlib
```
3. Clone this repository or download the source files.

## Usage

1. Open a terminal or command prompt in the directory containing the source files.
2. Run the application using the command:
```BASH
python main.py
```
3. Follow the on-screen prompts to perform various analyses on the CTA L ridership data.

## Features
The CTA L Analysis App supports the following features:
* Displaying general statistics about the dataset.
* Listing the top 10 busiest stations.
* Listing the least 10 busiest stations.
* Displaying stop and accessibility information for a specific line color.
* Displaying ridership data by month and by year.
* Comparing ridership data between two stations.
* Plotting ridership data for specific analyses.
* Displaying and plotting station locations for a specific line color.
