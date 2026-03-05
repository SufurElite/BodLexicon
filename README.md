# BodLexicon 

This code repository, developed for the Code the Collection Oxford Hackathon 2026, was developed with the aim of identifying dialect change in given transcribed manuscripts with the proof of concept being done for the Vernon Manuscript, Piers Plowman poem. 

It provides a reproducible framework from which to recreate the experiments in a containerized environment (for ease of both local and remote ddeployment) and a proof-of-concept for subsequent work in the area.

## How to run

As of now, you can either run the code by creating a python environment as follows below or through creating the container as follows afterwards. And, once the server is running, you can open the html file found in the frontend directory. 

### Python Environment

For this project, I recommend using python version 3.10 (and strongly suggest you use the containerized approach).

```bash
python -m venv .venv 
. .venv/bin/activate
pip -r requirements.txt
# and after installing the requirements you can either immediately launch the server with the premade variants.db
# or by rerunning the preprocessing procedure and recreating it (I show recreating it first)
cd BodLexicon/preprocessing 
python main.py 
cd ../app
python application.py
```

### A Containerized Approach

For the containerized approach, I would recommend using Podman (or Docker if you prefer) as follows:

```bash
podman build -t bodlexicon .
podman container runlabel RUN localhost/bodlexicon:latest
```

## How it works

As an overview, the pipeline (and project as a whole) works as follows:
* Data collection
    * Pulled the data from the Bodleian’s IIIF compliant manuscript dataset
    * Built a modifiable filtering scheme to extract desired relevant subsets 
* Preprocessing
    * Removed ¶ and // , marked words that were fully bracketed, marked abbreviation notes in the middle of words, removed Roman numerals
* The algorithm
    * Removed all the stop words from the texts
    * Created a frequency map of the words
    * Ran a modified version of Levenshtein’s distance to identify words that were similar
    * Stored our word pairs, frequency map, and initial manuscripts in a sqlite database 

### Database Schema

Here is the schema for the generated database: 

<b> Manuscripts: </b>

_Primary Key is the title_

| Variable Name | Value Type    | Description                                                                                | 
| ------------- | ------------- | ------------------------------------------------------------------------------------------ |
| title         | TEXT          | The title of the document (label in the metadata).                                         |
| text          | TEXT          | The text extracted from the html in the title.                                             | 

<b> Variants: </b>

_Primary Key is the word_

| Variable Name | Value Type    | Description                                                                                | 
| ------------- | ------------- | ------------------------------------------------------------------------------------------ |
| word          | TEXT          | A given word in the vocabulary                                                             |
| count         | INT           | The number of occurrences it has in the corpus                                             | 

<b> Variant Occurrences: </b>

_Primary Key is the composite key of the word and the manuscript it in which occurs_ 

| Variable Name    | Value Type    | Description                                                                                | 
| -------------    | ------------- | ------------------------------------------------------------------------------------------ |
| word             | TEXT          | The word in question                                                                       |
| manuscript_title | TEXT          | The manuscript title in which the word was found                                           | 

<b> Word Pairs           </b>

_Primary Key is the word\_a_

| Variable Name    | Value Type    | Description                                                                                | 
| -------------    | ------------- | ------------------------------------------------------------------------------------------ |
| word_a           | TEXT          | The first word that the algorithm found similar to word b                                  |
| word_b           | TEXT          | The word found similar to word_a by the algorithm                                          | 

This table is inherently symmetric, which at some point would be good to half.


## To-Dos

- [ ] Enable multilingual support, identification of language within the text and relevant glossary usage 
- [ ] Look into different phonetic variations as well as areas of morphological explanation that can be included
- [ ] Host the website
- [ ] Select appropriate license and contributing md file
