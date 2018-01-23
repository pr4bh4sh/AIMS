# Automation Infrastructure Management Server

## Running project
1. Install virtualenv
2. Install pip modules from requirements.txt
3. Start server `flask aims/server.py`

## TO-DO

### Endpoints

1. []  /services (filter out services not available for os)
1. []  /androidlist
1. []  /startandroidemu
1. []  /ioslist
1. []  /startiossim
1. []  /listappiumserverurl
1. []  /getserverlog
1. []  /getadblog(post/get device id)
1. []  /killallappiumserver
1. []  /killandroidemu
1. []  /killiossim
1. []  /installappiumserver
1. []  /uninstallappiumserver(post/get version)
1. []  /uploadapk
1. []  /uploadipa
1. []  /listandroidapps
1. []  /listiosapps
1. []  /uploadmiscfile
1. []  /listallfiles
1. []  /uploadsimapp
1. []  /deletefiles
1. []  /streamdesktop (far fetched for now)
1. []  /createdroidemu(post json)
1. []  /createiossim(post)
1. []  /reboot
1. []  /showresultslist
1. []  /uploadresultsto

## Task
1. [] Change virtualenv+pip to pipenv.
1. []  Create DB log (use flaskSQLAlchemy)
1. []  Use libs (as much as possible, less reinventing)
1. []  Write tests
1. []  Implement User level(no of device available, authtoken, rate limiter)
1. []  Proxying webdriver endpoint (too early to think)
