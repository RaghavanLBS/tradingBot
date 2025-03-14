
from playwright.sync_api import sync_playwright
import log

url = "https://trendlyne.com/macro-data/fii-dii/latest/snapshot-pastmonth"


def createScreenshot_and_get_fii_data(url):
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            log.info("creating screenshot using playwright")
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto(url)
            fiiEquity =  page.get_by_text('FII Total').nth(1)
            fiiEquity.scroll_into_view_if_needed()
            fiiProvisional = page.locator('#cash-pastmonth')
            page.screenshot(path=f'FII-DII-{browser_type.name}.png')
            fiiEquity =  page.locator('#fii-pastmonth')
            fiiEquity.click()
            page.screenshot(path=f'FII-EQUITY-{browser_type.name}.png')
            
            browser.close() 
            log.info("SCreenshot created for FII-DII-x and FII-Equity pngs with trendlyne")
        
def create5dayScreenshotforNifty(date):
    url = "https://www.google.com/finance/quote/NIFTY_50:INDEXNSE?window=5D"
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)
            image_path = f'.\\nifty\\5-day_nifty-{date}.png'
            page.screenshot(path=image_path)
           
            
            browser.close() 
            log.info("Screenshot created for 5 day nifty")
        
            return image_path

def createIntradayScreenshot_indicators(data):
    url = 'https://finance.yahoo.com/chart/%5ENSEI#eyJsYXlvdXQiOnsiaW50ZXJ2YWwiOjEsInBlcmlvZGljaXR5IjoxLCJ0aW1lVW5pdCI6Im1pbnV0ZSIsImNhbmRsZVdpZHRoIjoyLjU1Mjc3NDgzNDczMzAyNSwiZmxpcHBlZCI6ZmFsc2UsInZvbHVtZVVuZGVybGF5Ijp0cnVlLCJhZGoiOnRydWUsImNyb3NzaGFpciI6dHJ1ZSwiY2hhcnRUeXBlIjoibW91bnRhaW4iLCJleHRlbmRlZCI6ZmFsc2UsIm1hcmtldFNlc3Npb25zIjp7fSwiYWdncmVnYXRpb25UeXBlIjoib2hsYyIsImNoYXJ0U2NhbGUiOiJsaW5lYXIiLCJzdHVkaWVzIjp7IuKAjHZvbCB1bmRy4oCMIjp7InR5cGUiOiJ2b2wgdW5kciIsImlucHV0cyI6eyJTZXJpZXMiOiJzZXJpZXMiLCJpZCI6IuKAjHZvbCB1bmRy4oCMIiwiZGlzcGxheSI6IuKAjHZvbCB1bmRy4oCMIn0sIm91dHB1dHMiOnsiVXAgVm9sdW1lIjoiIzBkYmQ2ZWVlIiwiRG93biBWb2x1bWUiOiIjZmY1NTQ3ZWUifSwicGFuZWwiOiJjaGFydCIsInBhcmFtZXRlcnMiOnsiY2hhcnROYW1lIjoiY2hhcnQiLCJlZGl0TW9kZSI6dHJ1ZSwicGFuZWxOYW1lIjoiY2hhcnQifSwiZGlzYWJsZWQiOmZhbHNlfSwi4oCMbWFjZOKAjCAoMTIsMjYsOSkiOnsidHlwZSI6Im1hY2QiLCJpbnB1dHMiOnsiRmFzdCBNQSBQZXJpb2QiOjEyLCJTbG93IE1BIFBlcmlvZCI6MjYsIlNpZ25hbCBQZXJpb2QiOjksImlkIjoi4oCMbWFjZOKAjCAoMTIsMjYsOSkiLCJkaXNwbGF5Ijoi4oCMbWFjZOKAjCAoMTIsMjYsOSkifSwib3V0cHV0cyI6eyJNQUNEIjoiYXV0byIsIlNpZ25hbCI6IiNGRjAwMDAiLCJJbmNyZWFzaW5nIEJhciI6IiMwMEREMDAiLCJEZWNyZWFzaW5nIEJhciI6IiNGRjAwMDAifSwicGFuZWwiOiLigIxtYWNk4oCMICgxMiwyNiw5KSIsInBhcmFtZXRlcnMiOnsiY2hhcnROYW1lIjoiY2hhcnQiLCJlZGl0TW9kZSI6dHJ1ZX0sImRpc2FibGVkIjpmYWxzZX0sIuKAjHJzaeKAjCAoMTQpIjp7InR5cGUiOiJyc2kiLCJpbnB1dHMiOnsiUGVyaW9kIjoxNCwiRmllbGQiOiJmaWVsZCIsImlkIjoi4oCMcnNp4oCMICgxNCkiLCJkaXNwbGF5Ijoi4oCMcnNp4oCMICgxNCkifSwib3V0cHV0cyI6eyJSU0kiOiJhdXRvIn0sInBhbmVsIjoi4oCMcnNp4oCMICgxNCkiLCJwYXJhbWV0ZXJzIjp7InN0dWR5T3ZlclpvbmVzRW5hYmxlZCI6dHJ1ZSwic3R1ZHlPdmVyQm91Z2h0VmFsdWUiOjgwLCJzdHVkeU92ZXJCb3VnaHRDb2xvciI6ImF1dG8iLCJzdHVkeU92ZXJTb2xkVmFsdWUiOjIwLCJzdHVkeU92ZXJTb2xkQ29sb3IiOiJhdXRvIiwiY2hhcnROYW1lIjoiY2hhcnQiLCJlZGl0TW9kZSI6dHJ1ZX0sImRpc2FibGVkIjpmYWxzZX0sIuKAjFN1cGVydHJlbmTigIwgKDcsMykiOnsidHlwZSI6IlN1cGVydHJlbmQiLCJpbnB1dHMiOnsiUGVyaW9kIjo3LCJNdWx0aXBsaWVyIjozLCJpZCI6IuKAjFN1cGVydHJlbmTigIwgKDcsMykiLCJkaXNwbGF5Ijoi4oCMU3VwZXJ0cmVuZOKAjCAoNywzKSJ9LCJvdXRwdXRzIjp7IlVwdHJlbmQiOiIjOGNjMTc2IiwiRG93bnRyZW5kIjoiI2I4MmMwYyJ9LCJwYW5lbCI6ImNoYXJ0IiwicGFyYW1ldGVycyI6eyJjaGFydE5hbWUiOiJjaGFydCIsImVkaXRNb2RlIjp0cnVlfSwiZGlzYWJsZWQiOmZhbHNlfX0sInBhbmVscyI6eyJjaGFydCI6eyJwZXJjZW50IjowLjY0LCJkaXNwbGF5IjoiXk5TRUkiLCJjaGFydE5hbWUiOiJjaGFydCIsImluZGV4IjowLCJ5QXhpcyI6eyJuYW1lIjoiY2hhcnQiLCJwb3NpdGlvbiI6bnVsbH0sInlheGlzTEhTIjpbXSwieWF4aXNSSFMiOlsiY2hhcnQiLCLigIx2b2wgdW5kcuKAjCJdfSwi4oCMbWFjZOKAjCAoMTIsMjYsOSkiOnsicGVyY2VudCI6MC4xNiwiZGlzcGxheSI6IuKAjG1hY2TigIwgKDEyLDI2LDkpIiwiY2hhcnROYW1lIjoiY2hhcnQiLCJpbmRleCI6MSwieUF4aXMiOnsibmFtZSI6IuKAjG1hY2TigIwgKDEyLDI2LDkpIiwicG9zaXRpb24iOm51bGx9LCJ5YXhpc0xIUyI6W10sInlheGlzUkhTIjpbIuKAjG1hY2TigIwgKDEyLDI2LDkpIl19LCLigIxyc2nigIwgKDE0KSI6eyJwZXJjZW50IjowLjE5OTk5OTk5OTk5OTk5OTk2LCJkaXNwbGF5Ijoi4oCMcnNp4oCMICgxNCkiLCJjaGFydE5hbWUiOiJjaGFydCIsImluZGV4IjoyLCJ5QXhpcyI6eyJuYW1lIjoi4oCMcnNp4oCMICgxNCkiLCJwb3NpdGlvbiI6bnVsbH0sInlheGlzTEhTIjpbXSwieWF4aXNSSFMiOlsi4oCMcnNp4oCMICgxNCkiXX19LCJzZXRTcGFuIjp7Im11bHRpcGxpZXIiOjEsImJhc2UiOiJ0b2RheSIsInBlcmlvZGljaXR5Ijp7ImludGVydmFsIjoxLCJwZXJpb2QiOjEsInRpbWVVbml0IjoibWludXRlIn0sInNob3dFdmVudHNRdW90ZSI6dHJ1ZX0sIm91dGxpZXJzIjpmYWxzZSwiYW5pbWF0aW9uIjp0cnVlLCJoZWFkc1VwIjp7InN0YXRpYyI6dHJ1ZSwiZHluYW1pYyI6ZmFsc2UsImZsb2F0aW5nIjpmYWxzZX0sImxpbmVXaWR0aCI6MiwiZnVsbFNjcmVlbiI6dHJ1ZSwic3RyaXBlZEJhY2tncm91bmQiOnRydWUsImNvbG9yIjoiIzAwODFmMiIsImNyb3NzaGFpclN0aWNreSI6ZmFsc2UsImRvbnRTYXZlUmFuZ2VUb0xheW91dCI6dHJ1ZSwic3ltYm9scyI6W3sic3ltYm9sIjoiXk5TRUkiLCJzeW1ib2xPYmplY3QiOnsic3ltYm9sIjoiXk5TRUkiLCJxdW90ZVR5cGUiOiJJTkRFWCIsImV4Y2hhbmdlVGltZVpvbmUiOiJBc2lhL0tvbGthdGEiLCJwZXJpb2QxIjoxNzQxNTgxMDAwLCJwZXJpb2QyIjoxNzQxNzUzODAwfSwicGVyaW9kaWNpdHkiOjEsImludGVydmFsIjoxLCJ0aW1lVW5pdCI6Im1pbnV0ZSIsInNldFNwYW4iOnsibXVsdGlwbGllciI6MSwiYmFzZSI6InRvZGF5IiwicGVyaW9kaWNpdHkiOnsiaW50ZXJ2YWwiOjEsInBlcmlvZCI6MSwidGltZVVuaXQiOiJtaW51dGUifSwic2hvd0V2ZW50c1F1b3RlIjp0cnVlfX1dLCJyYW5nZSI6bnVsbH0sImV2ZW50cyI6eyJkaXZzIjp0cnVlLCJzcGxpdHMiOnRydWUsInRyYWRpbmdIb3Jpem9uIjoibm9uZSIsInNpZ0RldkV2ZW50cyI6W119LCJwcmVmZXJlbmNlcyI6e319'        

def createIntradayTickerScreenshot(ticket, filename):
    url = f"https://www.google.com/finance/quote/{ticket}"
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto(url)
            image_path = filename
            page.screenshot(path=image_path)
            
            browser.close() 
            return image_path

def create5dayTickerScreenshot(ticket,filename):
    url = f"https://www.google.com/finance/quote/{ticket}?window=5D"
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)
            
            page.screenshot(path=filename)
            
            browser.close() 
            log.info("Screenshot created for 5 day nifty")
        
            return filename
        

def create5dayUSDJI(filename):
    url = f"https://www.google.com/finance/quote/.IXIC:INDEXNASDAQ?window=5D"
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)
            image_path = filename
            page.screenshot(path=image_path)
            
            browser.close() 
            log.info("Screenshot created for 5 day nifty")
        
            return image_path

def createIntradayUSDJI(image_path):
    url = f"https://www.google.com/finance/quote/.IXIC:INDEXNASDAQ"
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)
            
            page.screenshot(path=image_path)
            
            browser.close() 
            log.info("Screenshot created for 5 day nifty")
        
            return image_path
        
def createScreenshotforIntradayNifty(filename):
    url = "https://www.google.com/finance/quote/NIFTY_50:INDEXNSE"
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto(url)
            image_path = filename
            page.screenshot(path=image_path)
            
            browser.close() 
            return image_path

