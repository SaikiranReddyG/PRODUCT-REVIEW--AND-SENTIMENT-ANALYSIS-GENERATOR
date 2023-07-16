# PRODUCT-REVIEW--AND-SENTIMENT-ANALYSIS-GENERATOR

This project aims to perform sentiment analysis on product reviews from Flipkart.com. It collects data from the website, analyzes the sentiment of each comment, and provides visualizations such as word clouds and sentiment counts.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Contributing](#contributing)


## Introduction

This application collects data from Flipkart.com by searching for specific products. It retrieves product details, customer names, ratings, comment headings, and comments. It then performs sentiment analysis on the comments using the [NLTK](https://www.nltk.org/) library and classifies them as positive or negative.

The application also generates a word cloud based on the comments and provides a downloadable CSV file containing the collected data for further analysis.

## Installation

1. Clone the repository:
https://github.com/SaikiranReddyG/PRODUCT-REVIEW-GENERATOR.git

2. Install the required dependencies:
Flask==2.0.1
matplotlib==3.4.3
nltk==3.6.3
pandas==1.3.3
requests==2.26.0
beautifulsoup4==4.9.3
wordcloud==1.8.1
Flask-Cors==3.0.10

## Usage

1. Run the Flask application:

2. Access the application in your web browser at suggeste host
3. Enter a search query for the desired product and submit the form.
4. The application will retrieve the product details, perform sentiment analysis on the comments, generate a word cloud, and display the results.

## Results

The application provides the following results:

- Sentiment Analysis: The sentiment of each comment is classified as positive or negative.
- Word Cloud: A visual representation of the most frequent words in the comments.
- Downloadable CSV: The collected data in CSV format for further analysis.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.






