R2D2
====
Tiny CI system for Android based on BuildBot

Using R2D2 is really straightforward, to start R2D2 just run start.sh script, to stop run stop.sh script.

To configure R2D2 just define a config.py file into master/ folder, remember to define all fields required, e.g.:

    AUTH_USER = "pyflakes"
    AUTH_PSW = "pyflakes"

    SLAVE_NAME="example-slave"
    SLAVE_PSW="pass"

    MAIL_USER="dunno@gmail.com"
    MAIL_PSW="dunno"

    MAIL_RECIPIENTS = ["stagi.andrea@gmail.com"]

    REPOSITORY="git@github.com:test/test.git"

    APP_NAME = "My app name"

    RELEASE_STEP = "./gradlew release;"
    MAKE_STEP = "./gradlew assembleDebug;"
    TEST_STEP = "./gradlew test;"

    ANDROID_HOME = "/Users/dunno/android-sdk"

    BUILDBOT_PORT = 8010