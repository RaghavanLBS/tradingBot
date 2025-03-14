import olama

## Introduction
response = olama.chat(
    model='llava:13b',  # or 'llava:7b'
    messages=[
        (
            'role': 'user',
            'content': 'Describe this image.'
        )
    ],
    images=['./FII-DII-chromium.png']
)

## Introduction
print(response['message']['content'])