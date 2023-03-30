import json, os

# collect info about files
collection = []

# iterate over json files in directory
for filename in os.listdir():
    if filename.endswith('.json') and not filename == 'collection.json':
        print(filename)
        with open(filename, 'r') as f:
            content = json.load(f)

        input_data = content['data']
        output_data = content['response']
        messages = input_data['messages']
        assembled = '\n\n'.join('\n'.join([f'{k}:{v}' for k,v in mess.items()]) for mess in messages)

        prompt_tokens = output_data['usage']['prompt_tokens']
        completion_tokens = output_data['usage']['completion_tokens']

        ai_output = output_data['choices'][0]['message']['content']
        
        collection.append({
            'prompt': assembled,
            'prompt_tokens': prompt_tokens,
            'ai_output': ai_output,
            'ai_output_tokens': completion_tokens,
        })

# save to json
with open('collection.json', 'w') as f:
    json.dump(collection, f, indent=4)

factors = []
# compare token counts to naive counting methods.
for item in collection:
    prompt = item['prompt']
    ai_output = item['ai_output']
    prompt_tokens = item['prompt_tokens']
    ai_output_tokens = item['ai_output_tokens']
    
    prompt_guess = len(prompt.split(' '))
    ai_output_guess = len(ai_output.split(' '))
    
    # store triplets of (length, actual, guess)
    factors.append((len(prompt), prompt_tokens, prompt_guess))
    factors.append((len(ai_output), ai_output_tokens, ai_output_guess))

# compare length of text to accuracy of token count
# sort by length of text
factors = sorted(factors, key=lambda x: x[0])
for triplet in factors:
    print(triplet[0], triplet[1]/triplet[2])

# conclusion: with over 4k chars, the fraction of tokens to words is probably about 1.2, as it goes from 1.1 to 1.3 between 500 and 4k chars, and is stable-ish around 1.2.
