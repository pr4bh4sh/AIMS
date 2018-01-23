# Automation Infrastructure Management Server

## Running project

1. Install python3 `brew install python3`
1. Execute `sh setup.sh` to setup the environment
1. Execute `python3 aims/server.py` to run the flask server
1. Open [http://127.0.0.1:8090](http://127.0.0.1:8090) to see the available services

## TO-DO

### Endpoints

1. [x]  /services (filter out services not available for os)
1. [ ]  /androidlist
1. [ ]  /startandroidemu
1. [ ]  /ioslist
1. [ ]  /startiossim
1. [ ]  /listappiumserverurl
1. [ ]  /getserverlog
1. [ ]  /getadblog(post/get device id)
1. [ ]  /killallappiumserver
1. [ ]  /killandroidemu
1. [ ]  /killiossim
1. [ ]  /installappiumserver
1. [ ]  /uninstallappiumserver(post/get version)
1. [ ]  /uploadapk
1. [ ]  /uploadipa
1. [ ]  /listandroidapps
1. [ ]  /listiosapps
1. [ ]  /uploadmiscfile
1. [ ]  /listallfiles
1. [ ]  /uploadsimapp
1. [ ]  /deletefiles
1. [ ]  /streamdesktop (far fetched for now)
1. [ ]  /createdroidemu(post json)
1. [ ]  /createiossim(post)
1. [ ]  /reboot
1. [ ]  /showresultslist
1. [ ]  /uploadresultsto

## Task
1. [x] Change virtualenv+pip to pipenv.
1. [ ]  Create DB log (use flaskSQLAlchemy)
1. [ ]  Use libs (as much as possible, less reinventing)
1. [ ]  Write tests
1. [ ]  Publish the library in pypi
1. [ ]  Implement User level(no of device available, authtoken, rate limiter)
1. [ ]  Proxying webdriver endpoint (too early to think)
