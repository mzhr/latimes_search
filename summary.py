# Functions to process summary 

import string
from difflib import SequenceMatcher

def print_summary(doc_file, seek_pos, queries, lexicon, query_summary):
    lines = get_doc(doc_file, seek_pos)
    if query_summary:
        summary_list = rank_lines(query_score, lines, queries, lexicon)
    else:
        summary_list = rank_lines(feature_score, lines, queries, lexicon)
    print build_summary(summary_list)
    print ""


def get_doc(doc_file, location):
    # Parse through the document file returning paragraph of section and lines
    parsing_block = {"<HEADLINE>": 0, 
                     "<BYLINE>": 1, 
                     "<TEXT>": 2, 
                     "<GRAPHIC>": 3 }
    lines = [""]*len(parsing_block)
    block = 0

    # Open document file to parse
    doc_file.seek(location, 0)
    line = doc_file.readline().strip()
    summary_flag = False

    # Parse the document in the document file
    for line in iter(doc_file.readline, ''):
        # Strip read in the next line and remove new line characters
        line = line.strip("\n")

        # Stop at document closing tags
        if line == "</DOC>":
            break

        # Close parsing tags
        if (line == "</HEADLINE>" or line == "</BYLINE>" 
                or line == "</TEXT>" or line == "</GRAPHIC>"):
            summary_flag = False

        # Parse line if flag is true
        if (summary_flag == True and line != "<P>" 
                and line != "</P>" and "<TABLE" not in line):
            lines[block] += line

        # Start parsing and declare segment of document it is
        if line in parsing_block:
            summary_flag = True
            block = parsing_block[line]

    return [sentences.split(". ") for sentences in lines]


def rank_lines(ranking_function, paragraphs, query, lexicon):
    # Create list of sentences distanced on paragraphs
    lines = []
    for paragraph in paragraphs:
        lines += paragraph

    # Calulate the scores for each sentence
    line_scores = [0] * len(lines)
    for line in range(len(lines)):
        line_scores[line] = ranking_function(query, lines, line, 
                                             paragraphs[0], lexicon)
    ranked_summaries = zip(line_scores, lines, range(len(lines)))

    # Pick top 3 sentences and sort in sentence order
    print_count = 3 if len(ranked_summaries) > 3 else len(ranked_summaries)
    ranked_summaries = sorted(ranked_summaries, key=lambda x: x[0], reverse=True)
    ranked_summaries = sorted(ranked_summaries[:print_count], key=lambda x: -x[2])
    ranked_summaries = [line[1:] for line in ranked_summaries if line[1] != None]
    return ranked_summaries


def feature_score(query, lines, n, header_sentences, lexicon):
    score = 0.0

    # feature 1: position in document, higher score, earlier sentences
    score += 1.0/(n+1.0)

    # feature 2-3: uniqueness of context, jaccard of before and after sentences
    current = (''.join([current.lower() for current in lines[n]])).split()
    current = [word.translate(None,string.punctuation).strip() 
               for word in current]
    if n+1 < len(lines)-1:
        after = (''.join([after.lower() for after in lines[n+1]])).split()
        after = [word.translate(None,string.punctuation).strip() 
                 for word in after]
        score -= ((len(set(after).intersection(set(current))) / 
                    (len(set(after).union(set(current)))+1.0)))
    if n-1 >= 0:
        previous = (''.join([previous.lower() for previous in lines[n-1]])).split()
        previous = [word.translate(None,string.punctuation).strip() 
                    for word in previous]
        score -= ((len(set(previous).intersection(set(current))) / 
                    (len(set(previous).union(set(current)))+1.0)))

    # feature 4: Low number of special characters (not - ' , ? / ( ) ! $ .)
    score -= SequenceMatcher(None, lines[n], "_*&^%#@~`\][|}{;:><").ratio()*100.0

    # feature 5: Higher preference to que words
    cue_words = ["incidentally", "example", "anyway", "furthermore", "first", 
                 "second", "then", "now", "thus", "moreover", "therefore", 
                 "hence", "lastly", "finally", "summary"]
    for word in cue_words:
        if word in lines[n].lower():
            score += 0.3
            break

    # feature 6: Keyword count squared over length of sentence
    keywords_count = 0.0
    for word in lines[n].split():
        if word in lexicon and lexicon[word][2] > 100 and lexicon[word][2] < 10000: 
            keywords_count += 1.0
    score += (keywords_count**2.0)/(len(lines[n])+1.0)

    # feature 7: Jaccard similarity of header and sentence
    header_words = (''.join([after.lower() for after in header_sentences])).split()
    header_words = [word.translate(None,string.punctuation).strip() 
                    for word in header_words]
    relation = (len(set(current).intersection(set(header_words))) / 
                (len(set(current).union(set(header_words)))+1.0))
    if relation < 0.7:
        score += relation

    # feature 8?: Remove empty stings
    if lines[n] == "":
        score -= 100

    # feature 9-15: Non summary words (Anaphoric, Honorifics, Negations, Auxilary, 
    #                               Vague descripters, Conjunctions, Prepositions)
    # Based on J. Goldstein '99
    goldstein_categories = {"anaphoric": [0, 0.01],
                            "honorific": [1, 0.3],
                            "negation": [2, 0.1],
                            "auxilary": [3, 0.5],
                            "vague": [4, 0.5],
                            "conjunction": [5, 0.01],
                            "preposition": [6, 0.001]
                            }
    nonsummary_goldstein = [["these", "this", "those"], ["dr", "mr", "mrs"],
                          ["no", "dont", "never"], ["was", "could", "did"],
                          ["often", "about", "significant", "some", "several"],
                          ["and", "or", "but", "so", "although", "however"],
                          ["at", "by", "for", "of", "in", "to", "with"]]
    nonsummary_score = 0.0
    for word in lines[n].split():
        for name, category in goldstein_categories.items():
            if word.lower() in nonsummary_goldstein[category[0]]:
                nonsummary_score -= category[1]
    score -= (nonsummary_score)/len(goldstein_categories)

    
    return score


def query_score(query, lines, n, headerwords, lexicon):
    score = 0.0
    
    # Clean query and line for comparison
    cleaned_query = (' '.join([after.lower() for after in query])).split()
    cleaned_query = [word.translate(None,string.punctuation).strip() 
                     for word in cleaned_query]
    cleaned_line = (''.join([after.lower() for after in lines[n]])).split()
    cleaned_line = [word.translate(None,string.punctuation).strip() 
                     for word in cleaned_line]

    # (Unique query in word^2)/count of queries
    query_count = 0.0
    for q in cleaned_query:
        if q in cleaned_line:
            query_count +=0.5
    score += (query_count**2.0)/(len(cleaned_query))

    # Combine with features (Ignored for now for evaluation)
    # score += feature_score(query, lines, n, headerwords, lexicon)*0.01
    return score 


def build_summary(ranked_summaries):
    summary = ""

    if ranked_summaries[0][1] > 1:
        summary += "..."

    # Build summary adding '...' if distance in document
    for line in ranked_summaries:
        summary += line[0].strip() + ". "
        current = line[1]

    # Rebuild summary if length is too long making hard break to nearest word
    if len(summary) > 500:
        break_summary = ""
        for word in summary.split():
            break_summary += word
            if len(break_summary) > 480:
                summary = break_summary + "..."
                break
            else:
                break_summary += " "

    return summary
