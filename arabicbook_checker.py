import requests
import re
import os
import openai

tokens=[]

def check_quran(line):
    # Set the query parameter
    query = line
    if "إهدنا الصراط المستقيم" in query:
        return f"{query}"
    elif "الرحمن الرحيم" in query:
        return f"{query}"
    elif "مالك يوم الدين" in query:
        return f"{query}"
    elif "إياك نعبد وإياك نستعين" in query:
        return f"{query}"
    elif "الحمد لله رب العالمين" in query:
        return f"{query}"
    elif query == "آمين":
        return "آمين"
    elif "بسم الله الرحمن الرحيم" in query:
        return "بسم الله الرحمن الرحيم"
    elif "الله أكبر" in query:
        return "الله أكبر"
    elif "أعوذ بالله من الشيطان الرجيم" in query:
        return "أعوذ بالله من الشيطان الرجيم"

    # Set the API endpoint URL
    url = 'https://www.alfanous.org/api/search'

    # Set the request parameters
    params = {'query': query}

    # Make the request and retrieve the response
    response = requests.get(url, params=params)

    # Parse the response as JSON and extract the text_no_highlight key from the first hit
    results = response.json()
    if results["search"]["ayas"]:
        text_no_highlight = results["search"]["ayas"]["1"]["aya"]["text_no_highlight"]
        surah_number = results["search"]["ayas"]["1"]["identifier"]["sura_id"]
        ayah_number = results["search"]["ayas"]["1"]["identifier"]["aya_id"]
    else:
        return "error"
    

    # Split the short string into words
    short_words = query.split()

    if len(text_no_highlight.split()) - len(short_words) > 4: 
        prompt=f"{text_no_highlight}\n\nFrom the above verse, extract the portion in arabic that corresponds closest to: {query} \n\n\n:"

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt = prompt,
            temperature=0.3,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        
        # get text from json response
        text = response["choices"][0]["text"]

        # get total tokens from json response
        total_tokens = response["usage"]["total_tokens"]
        tokens.append(str(total_tokens))

        return f"{text} {surah_number}:{ayah_number}"
    
    else: 
        return f"{text_no_highlight} {surah_number}:{ayah_number}"
         
def check_quran_string(input_string):
    result_string = ""
    for line in input_string.split('\n'):
        if re.search(r'[\u0600-\u06FF]+', line):  # check if the line contains Arabic characters
            processed_line = check_quran(line)
            if processed_line == "error":
                result_string += "" + "\n"
            else:
                result_string += processed_line + "\n"
        else:
            result_string += line + "\n"

    # remove the extra newline character at the end of the string
    result_string = result_string[:-1]
    # sum all the tokens
    print(sum([int(i) for i in tokens]))
    return result_string


def translate_quran(line):

    translateprompt = f"""

    This is a quran verse. Please translate the verse accurately according to MS Abdul Haleem's translation.
    Don't include the arabic vowel markings in the output.

    {line}
    """ 

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt = translateprompt,
    temperature=0.3,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    text = response["choices"][0]["text"]

    return text

def translate_quran_string(input_string):
    result_string = ""
    for line in input_string.split('\n'):
        if re.search(r'[\u0600-\u06FF]+', line):  # check if the line contains Arabic characters
            processed_line = translate_quran(line)
            if processed_line == "error":
                result_string += "" + "\n"
            else:
                result_string += processed_line + "\n"
        else:
            result_string += "\n" + line 

    # remove the extra newline character at the end of the string
    result_string = result_string[:-1]

    return result_string








