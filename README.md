R2D2
====
Tiny CI system for Android based on BuildBot

Using R2D2 is really straightforward, to start R2D2 just run

    $ ./start.sh

script, to stop run

    $ ./stop.sh

To configure R2D2 just define a config.py file into master/ folder, remember to define all fields required, e.g.:

    AUTH_USER = "pyflakes"
    AUTH_PSW = "pyflakes"

    SLAVE_NAME="example-slave"
    SLAVE_PSW="pass"

    MAIL_USER="dunno@gmail.com"
    MAIL_PSW="dunno"
    MAIL_RECIPIENTS = ["stagi.andrea@gmail.com"]
    MAIL_USE_TLS=True
    MAIL_SMTP_HOST="smtp.gmail.com"
    MAIL_SMTP_PORT=587

    APP_NAME = "AppBeer"
    REPOSITORY="git@github.com:test/test.git"

    MAKE_STEP = "./gradlew assembleDebug;"
    TEST_STEP = "./gradlew test;"

    BUILD_LOCATION = "./build/outputs/apk/build-debug.apk"

    ANDROID_HOME = "/Users/dunno/android-sdk"

    BUILDBOT_HOST = 'http://testcustomhost'
    BUILDBOT_PORT = 8010

    HIPCHAT_TOKEN = 'myhipchattoken'
    HIPCHAT_ROOMS = ['myhipchatroom']

    NIGHTLY_TIME = [10,0]
    WEEKLY_TIME = [10,0,4]