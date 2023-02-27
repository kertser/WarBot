# Main library for WarBot

from transformers import AutoTokenizer ,AutoModelForCausalLM
import re
# Speller and punctuation:
import os
import yaml
import torch
from torch import package
# not very necessary
#import textwrap
from textwrap3 import wrap

# util function to get expected len after tokenizing
def get_length_param(text: str, tokenizer) -> str:
    tokens_count = len(tokenizer.encode(text))
    if tokens_count <= 15:
        len_param = '1'
    elif tokens_count <= 50:
        len_param = '2'
    elif tokens_count <= 256:
        len_param = '3'
    else:
        len_param = '-'
    return len_param

def remove_duplicates(S):
    S = re.sub(r'[a-zA-Z]+', '', S) #Remove english
    S = S.split()
    result = ""
    for subst in S:
        if subst not in result:
            result += subst+" "
    return result.rstrip()

def removeSigns(S):
    last_index = max(S.rfind("."), S.rfind("!"))
    if last_index >= 0:
        S = S[:last_index+1]
    return S

def prepare_punct():
    # Prepare the Punctuation Model
    # Important! Enable for Unix version (python related)
    # torch.backends.quantized.engine = 'qnnpack'
    torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
                                   'latest_silero_models.yml',
                                   progress=False)

    with open('latest_silero_models.yml', 'r') as yaml_file:
        models = yaml.load(yaml_file, Loader=yaml.SafeLoader)
    model_conf = models.get('te_models').get('latest')

    # Prepare punctuation fix
    model_url = model_conf.get('package')

    model_dir = "downloaded_model"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, os.path.basename(model_url))

    if not os.path.isfile(model_path):
        torch.hub.download_url_to_file(model_url,
                                       model_path,
                                       progress=True)

    imp = package.PackageImporter(model_path)
    model_punct = imp.load_pickle("te_model", "model")

    return model_punct

def initialize():
    """ Loading the model """
    fit_checkpoint = "WarBot"
    tokenizer = AutoTokenizer.from_pretrained(fit_checkpoint)
    model = AutoModelForCausalLM.from_pretrained(fit_checkpoint)
    model_punсt = prepare_punct()
    return (model,tokenizer,model_punсt)

def split_string(string,n=256):
    return [string[i:i+n] for i in range(0, len(string), n)]

def get_response(quote:str,model,tokenizer,model_punct,temperature=0.2):
    # encode the input, add the eos_token and return a tensor in Pytorch
    try:
        user_inpit_ids = tokenizer.encode(f"|0|{get_length_param(quote, tokenizer)}|" \
                                                      + quote + tokenizer.eos_token, return_tensors="pt")
        # Better to force the lenparameter to be = {2}
    except:
        return "Exception in tokenization" # Exception in tokenization

    chat_history_ids = user_inpit_ids # To be changed

    tokens_count = len(tokenizer.encode(quote))
    if tokens_count < 15:
        no_repeat_ngram_size = 2
    else:
        no_repeat_ngram_size = 1

    try:
        output_id = model.generate(
                    chat_history_ids,
                    num_return_sequences=1, # use for more variants, but have to print [i]
                    max_length=200, #512
                    no_repeat_ngram_size=no_repeat_ngram_size, #3
                    do_sample=True, #True
                    top_k=50,#50
                    top_p=0.9, #0.9
                    temperature = temperature, # was 0.6, 0 for greedy
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                    #device='cpu'
                )
    except:
        return "Exception" # Exception in generation

    response = tokenizer.decode(output_id[0], skip_special_tokens=True)
    response = removeSigns(response)
    response = response.split(quote)[-1]  # Remove the Quote
    response = re.sub(r'[^0-9А-Яа-яЁёa-zA-z;., !()/\-+:?]', '',
                      response)  # Clear the response, remains only alpha-numerical values
    response = remove_duplicates(re.sub(r"\d{4,}", "", response))  # Remove the consequent numbers with 4 or more digits
    response = re.sub(r'\.\.+', '', response) # Remove the "....." thing

    if len(response)>200:
        resps = wrap(response,200)
        for i in range(len(resps)):
            try:
                resps[i] = model_punct.enhance_text(resps[i], lan='ru')
                response = ''.join(resps)
            except:
                return "" # Excepion in punctuation
    else:
        response = model_punct.enhance_text(response, lan='ru')

    # Immanent postprocessing of the response
    response = re.sub(r'[UNK]', '', response)  # Remove the [UNK] thing
    response = re.sub(r',+', ',', response)  # Replace multi-commas with single one
    response = re.sub(r'-+', ',', response)  # Replace multi-dashes with single one
    response = re.sub(r'\.\?', '?', response)  # Fix the .? issue
    response = re.sub(r'\,\?', '?', response)  # Fix the ,? issue
    response = re.sub(r'\.\!', '!', response)  # Fix the .! issue
    response = re.sub(r'\.\,', ',', response)  # Fix the ,. issue
    response = re.sub(r'\.\)', '.', response)  # Fix the .) issue
    response = response.replace('[]', '') # Fix the [] issue

    return response

if __name__ == '__main__':
    """
    quote = "Здравствуй, Жопа, Новый Год, выходи на ёлку!"
    model, tokenizer, model_punct = initialize()
    response = ""
    while not response:
        response = get_response(quote, model, tokenizer, model_punct,temperature=0.2)
    print(response)
    """