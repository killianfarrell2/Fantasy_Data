#Import Libraries
from selenium import webdriver
import time
import pandas as pd
import os
from datetime import datetime

#Get Current time to be used to find run time at end of program
startTime = datetime.now()

#Import Premier League Results
prem_results_location = 'D:\\Football_Results_Downloads\\Historic_League_Results_E0_1993_2020.csv'
prem_results = pd.read_csv(prem_results_location)

#Select 2019/2020 season
prem_results_19_20 = prem_results.loc[prem_results['season_start_year'] == 2019]
#Get unique dates from column
dates = pd.DataFrame(prem_results_19_20.Date.unique(),columns = ['Date'])
#Convert to Datetime
dates = pd.to_datetime(dates['Date'], format='%Y-%m-%d') 

#Location of Chromedriver
chromedriver =  'D:\\Chromedriver\\chromedriver.exe'
#Set Parameters for Chromedriver
chromeOptions = webdriver.ChromeOptions()
#Create folder to download data to
download_folder = 'D:\\Chromedriver_Downloads\\'
if not os.path.exists(download_folder):
    os.makedirs(download_folder)
#Set default directory to download to
prefs = {"download.default_directory" : download_folder}
chromeOptions.add_experimental_option("prefs",prefs)
#Open browser window
browser = webdriver.Chrome(executable_path=chromedriver, options=chromeOptions)

#Open Login Page
url_login = 'https://www.fantrax.com/login'
browser.get(url_login)
browser.maximize_window()

#Import username and password from fantasy passwords file
with open('D:\\Passwords\\Fantasy_Password.txt') as f:
    username = f.readline()
    password = f.readline()

#Input Login credentials
Input_Username = browser.find_element_by_id('mat-input-0')
Input_Username.send_keys(username)
Input_Password = browser.find_element_by_id('mat-input-1')
Input_Password .send_keys(password)

#Copy Xpath from button after inspecting element
button_Xpath = '/html/body/app-root/div/div[1]/div/app-login/div/section/form/div[2]/button/span'
#Create click button object from above Xpath
Click_button = browser.find_elements_by_xpath(button_Xpath)
#Click button to log onto page
Click_button[0].click()

#put in 5 second delay so page can load
time.sleep(5)


#set parameters for Fantrax URL for Goalkeeper League
league_id_url = 'l3zwhakmk393b2sk'
view_url = 'STATS'
#Change position from outfield league
position_url = 'POS_704'
season_url = '19'
timeframe_url = 'BY_DATE'
max_results_url = '1000'
status_url = 'ALL'
scoring_cat_url = '5'
time_start_url = 'PERIOD_ONLY'
#Original file will be downloaded with this name
league_name = 'Goalkeeper'
#Rename File start name
file_start_name = 'Fantasy_goalkeeper_data_'

for date in dates:
    #Format date so it can be used in URL
    date_url = date.strftime('%Y-%m-%d') 
    #url of fantasy league with statistics
    url = ('https://www.fantrax.com/fantasy/league/'+league_id_url+'/players'
       +';view='+view_url
       +';positionOrGroup='+position_url
       +';seasonOrProjection=SEASON_9'+season_url
       +'_BY_DATE;timeframeTypeCode='+timeframe_url
       +';maxResultsPerPage='+max_results_url
       +';statusOrTeamFilter='+status_url
       +';scoringCategoryType='+scoring_cat_url
       +';timeStartType='+time_start_url
       +';startDate='+date_url
       +';endDate='+date_url)
   #Open url with browser    
    browser.get(url)
       
    #put in delay so once page loads button will be clicked
    time.sleep(15)
    
    #Download csv file into download folder
    download_button_Xpath ='/html/body/app-root/div/div[1]/div/app-league-players/div/section/filter-panel/div/div[5]/div[3]/button[1]/span'
    download_button = browser.find_elements_by_xpath(download_button_Xpath)
    download_button[0].click()
    
    #put in 5 second delay so file can download before renaming file
    time.sleep(5)
    
    #Rename file
    Filename = download_folder+file_start_name+date_url+'.csv'
    os.rename(download_folder+'Fantrax-Players-'+league_name+'.csv',Filename )

#Close Browser Window once loop ends
browser.close()

#Create dataframe to store results
combined_player_data = pd.DataFrame()

#Loop through all files in download folder
for file in os.listdir(download_folder):
    #Get filename
     filename = os.fsdecode(file)
     #import csv into dataframe
     csv_file = download_folder + filename
     data = pd.read_csv(csv_file)
     #Get Date of Data from filename
     file_date = filename[-14:-4]
     #Create Dataframe with date column
     file_date_df = pd.DataFrame([file_date]*len(data),columns = ['Date'])
     #Convert to Datetime
     file_date_df = pd.to_datetime(file_date_df['Date'], format='%Y-%m-%d')
     #Add Date column to data dataframe
     data = pd.concat([data,file_date_df], axis=1)
     #Append data to combined_player_data
     combined_player_data= combined_player_data.append(data, ignore_index = True)
     
#Create copy of combined_player_data
copy_data = combined_player_data.copy() 
#Remove any players who didn't play a game
copy_data = copy_data.loc[copy_data['GP'] != 0]
#Remove columns that are not needed
copy_data = copy_data.drop(['Rk','Status','Opponent','FP/G','% Owned','+/-'], axis=1)
#Reset Index
copy_data = copy_data.reset_index(drop=True)

#Get first date in dataset
min_date = copy_data['Date'].min().strftime('%Y-%m-%d') 
#Get last season end year
max_date = copy_data['Date'].max().strftime('%Y-%m-%d')     
#Filename of saved file
save_file_name = 'Fantasy_data_'+league_name+'_'+str(min_date)+'_'+str(max_date)+'.csv'
#Create folder to save data to
save_folder = 'D:\\Fantasy_data\\'
if not os.path.exists(save_folder):
    os.makedirs(save_folder)
#Save file to directory as csv
copy_data.to_csv(save_folder+save_file_name)

#Get run time
run_time = datetime.now() - startTime
print(run_time)