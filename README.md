# solarWeatherWebScraper
Project created for dad. 

# Description
Scrapes a website for solar weather information from last two hours. 

# Cron Job for MAC OS 
Pre-requisites: 
  - Make sure you don't execute this cron job as root user.
  - Make sure you set permissions to this file where only you can run & edit. ie chmod 700

steps to set up --> to run every two hours:
  - crontab -e
  - 0 */2 * * * /usr/bin/python3 /WhereeveryouPutThis/solarWeatherWebScraper/solarWeather.py >> /Users/yourUsername/cron_logs/solarWeather.log 2>&1
  - crontab -l --> verify that it has been added 
