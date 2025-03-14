from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import datetime
import email.message
import email.mime
import smtplib
import log,json,os
from json2html import *
gmail_username = os.getenv('gmail_username') 



gmail_key = os.getenv('gmail_key') 

 # Define these once; use them twice!
strFrom = os.getenv('gmail_from') 
strTo = os.getenv('gmail_To') 
strTo2 = os.getenv('gmail_To_2') 

def attach_images(msgRoot, image_list):
    # This example assumes the image is in the current directory
    #nifty_indicator_filename, nifty_5_day_image_path, nifty_intraday_image_path
    counter=1
    for image in image_list:
       
        fp = open(image, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', f'<image{counter}>')
        counter = counter+1
   
        msgRoot.attach(msgImage)
    return msgRoot

def send_email(signal, sentiment_json, fii_dii_json, bel_json,nifty_indicator_filename, nifty_5_day_image_path, nifty_intraday_image_path):

    

    # Convert JSON to HTML using json2html
    signal_html = json2html.convert(json = signal)
    bel_html = json2html.convert(bel_json)
    f_html = json2html.convert(fii_dii_json)
    sentiment_html=json2html.convert(sentiment_json)

    currentDate = datetime.datetime.today()
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = f'Trigger for NIFTY option Trade-{currentDate}'
    msgRoot['From'] = strFrom
    msgRoot['To'] = strTo
    img_css =''
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    content = f'''<div><b>Signal Received</b>:<div><span>{signal_html}</span></div> </div>
                  <div><b>Current BEL</b>:<div><span>{bel_html}</span></div> </div>
                    <br><div><b>Current NEWS sentiment summary</b>:<div><span>{sentiment_html}</span></div> </div>
                    <br><div><b>Current FII DII sentiment summary</b>:<div><span>{f_html}</span></div> </div>
                   
                    <br><div><b>Current NIFTY Indicators</b>:<div ><img style="width:100%; height=100%" src="cid:image1"/></div> </div>
                    <br><div><b> NIFTY Intraday day graph</b>:<div ><img style="width:100%; height=100%" src="cid:image2"/></div> </div>
                    <br><div><b> NIFTY 5 day graph</b>:<div ><img style="width:100%; height=100%" src="cid:image3"/></div> </div>
                     
                '''
    content = content + '''<style>
                        img  {width:100%; height:100%}
                    </style>'''
   
    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative =MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(content, 'html')
    msgAlternative.attach(msgText)
    msgRoot = attach_images(msgRoot, [nifty_indicator_filename, nifty_intraday_image_path,  nifty_5_day_image_path])
    
    # Send the email (this example assumes SMTP authentication is required)
    
    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo() # optional, called by login()
    server_ssl.login(gmail_username, gmail_key)  
    # ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
    server_ssl.sendmail(strFrom, strTo, msgRoot.as_string())
    #server_ssl.quit()
    server_ssl.close()
    log.info('successfully sent the mail')


