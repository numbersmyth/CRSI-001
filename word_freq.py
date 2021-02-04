#!/usr/bin/env python3

import argparse
import sys
import contextlib
import bs4 as bs
import urllib.request
from nltk.corpus import stopwords, words
from nltk import sent_tokenize
from nltk import download
from time import sleep
download('stopwords')

bsoup = bs.BeautifulSoup


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, bs.element.Comment):
        return False
    return True


def text_from_html(body):
    main_content = body.find("div", {'id': 'main-content'})
    children = main_content.findChildren(recursive=True)
    visible_texts = []
    for child in children:
        if tag_visible(child):
            text = child.string
            if text and ((len(text) > 1) or (len(text) == 1 and text.isalnum())):
                text = text.replace("\n", "")
                if text != '':
                    visible_texts.append(text)
    return visible_texts


def is_stop_word(word):
    if word.lower() in stopwords.words('english'):
        return True
    return False


# remove stopwords from text and then parse the text into dict of individual words and occurence count
def create_worddict_from_text(texts):
    worddict = {}
    for text in texts:
        newdict = dict.fromkeys(text.split(" "), 1)
        worddict = combine_into_maindict(newdict, worddict)

    # add every word into the word dict and give it a value or 1 occurance
    return worddict


# not yet implemented
#def extract_sentences_from_text(texts):
#    sentences = {}
#    for text in texts():
#        newdict = dict.fromkeys(nlth)


def dict_contains_word(word, wdict):
    for key in wdict.keys():
        if word == key:
            return True
    return False


def combine_into_maindict(newdict, maindict):
    for new_word in newdict.keys():
        if dict_contains_word(new_word, maindict):
            maindict[new_word] += 1
        else:
            maindict[new_word] = 1
    return maindict


def parse_scp_pages(startpage, pagecount):
    wordfreq_output = {}
    scp_url = "http://scp-wiki.wikidot.com/scp-"
    pagesref = range(startpage, startpage+pagecount)
    for pagenum in pagesref:
        if pagenum < 10:
            scp_id = "00"+str(pagenum)
        elif pagenum < 100:
            scp_id = "0"+str(pagenum)
        else:
            scp_id = str(pagenum)
        url = scp_url+scp_id
        print("Generating word list from "+scp_id)
        html = get_page_from_scpwiki(url)
        wordfreq_output = combine_into_maindict(create_worddict_from_text(text_from_html(html)), wordfreq_output)
    return wordfreq_output


def get_page_from_scpwiki(url):
    # maximum requests per minute is 240, meaning we can make 4 requests a second.
    sleep(0.25)
    with contextlib.closing(urllib.request.urlopen(url)) as resp:
        return bsoup(resp.read(), "html.parser")


def main(args):
    output = {}
    words = parse_scp_pages(int(args.starting_scp), int(args.ending_scp))
    for key in words.keys():
        if not is_stop_word(key):
            output[key] = words[key]
        else:
            print("STOPWORD: "+key)
    print(sorted(output, key=output.get, reverse=True))
    exit()


def _cli(args):
    parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    s_help = "Provide the starting SCP number. e.g. -s 99"
    e_help = "Provide the ending SCP number. -e 110"

    parser.add_argument('-s', '--starting-scp', help=s_help, required=True)
    parser.add_argument('-e', '--ending-scp', help=e_help, required=True)

    args = parser.parse_args()

    if not (args.starting_scp or args.ending_scp):
        print("Insufficient arguments. Please specify the starting and ending SCPs.")
        exit()

    return args


if __name__ == '__main__':
    main(_cli(sys.argv[1:]))
