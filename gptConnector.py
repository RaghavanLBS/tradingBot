import base64,os,log
import json
from mistralai import Mistral
from openai import OpenAIError
from openai import OpenAI

amma_api_key=''
trading_bot_type = 'Professional Trader'

trading_bot_conservativeness = 0.5

def extract_details_from_image(api_key, image_path, content):
    # Open and encode the image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Prepare the API request
    #url = "https://api.mistral.ai/v1/extract"  # Replace with the actual endpoint
    client = Mistral(api_key=api_key)

    
    # Define the messages for the chat
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": content
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}" 
                }
        ]
        }
    ]
    # Get the chat response
    chat_response = client.chat.complete(
        model="pixtral-12b-2409",
        messages=messages
    )

    # Print the content of the response
    return chat_response.choices[0].message.content



def extract_details_from_image_openai( image_path, content):
    # Open and encode the image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
   

    
    contents = [
        {"role": "system", "content": "You are a day  trading assistant who is specialized in providing buy signal and sell signal on options and equity."},
        {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": content
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    try:


        

        client = OpenAI(api_key =os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(model= "gpt-4o",
                                                messages= contents)
                                            
        summary = response.choices[0].message.content
        return summary
    except  OpenAIError as e:
        log.error(f"Open AI error:{e}")
        return -1


def get_buy_signal(sentiment_json, fii_dii_json, bel_json,nifty_indicator_filename, nifty_5_day_image_path, nifty_intraday_image_path):
    buy_json = -1
     # Open and encode the image
    with open(nifty_indicator_filename, "rb") as image_file:
        nifty_indicator_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    with open(nifty_5_day_image_path, "rb") as image_file:
        nifty_5_day_image = base64.b64encode(image_file.read()).decode('utf-8')
    with open(nifty_intraday_image_path, "rb") as image_file:
        nifty_intraday_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    response_json_format = '''
            <JSON>
                { 
                    "CE_BUY_POINT": At what point today it is good to buy nifty CE,
                    "CE_STOP_LOSS": At what point we take stop loss after CE buy  - only one point
                    "CE_PROFIT_POINT": At what point we take profit - only one point
                    "CE_OPTION_TO_BUY": Whcih NIFTY OPTION to buy give me option full script including next expiry date from zerodha. examples:  22300 CE, 22400 CE          
                    "PE_BUY_POINT": At what point today it is good to buy nifty PE,
                    "PE_STOP_LOSS": At what point we take stop loss after PE buy  - only one point
                    "PE_PROFIT_POINT": At what point we take profit - only one point 
                    "PE_OPTION_TO_BUY": Whcih NIFTY OPTION to buy give me option full script including next expiry date from zerodha. examples: 22300 PE, 22200 PE
                    "Preferred_Buying": PE or CE
               }
            </JSON>
    '''
    content = f'''
                I have collected data and news about NIFTY. Analyze those and then give me correct value of NIFTY option to buy.
                It can be PE or CE based on data.use only the information provided. Response should be enclosed with <JSON></JSON>
                JSON response format {response_json_format}
                Current Sentiment from News :{sentiment_json}
                FII DII Sell analysis [0 being negative sentiment and 1 being positive sentiment] : {fii_dii_json}
                BEL share looks like having correlation with NIFTY. so current BEL state :{bel_json}
                Apart from the above attaching image data for 5 day nifty, various nifty indicators and intraday nifty till now.
                Even though the preferred buying might be CE or PE, always give PE and CE buy points, stop losses and  and profit point
                Donot send anything other than JSON response. so it is easy to parse json from it

    '''
    contents = [
        {"role": "system", 
         "content": f"""You are a day trading assistant who is specialized in providing buy 
                    signal and sell signal on options and equity. 
                    You are {trading_bot_type}.
                    
                    
                    """
        },
        {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": content
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{nifty_indicator_image}"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{nifty_5_day_image}"
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{nifty_intraday_image}"
                    }

                }
            ]
        }
    ]

    try:

        print("Going to GPT -4o ")
        client = OpenAI(api_key =os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(model= "gpt-4o",
                                                messages= contents)
                                            
        summary = response.choices[0].message.content
        print(f"GPT returned summary{summary} ")
        return summary
    except  OpenAIError as e:
        log.error(f"Open AI error:{e}")
        print("Open AI error- could generate signal from GPT-4o")
        return -1
