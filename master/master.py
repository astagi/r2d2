import config
import hipchat

c = BuildmasterConfig = {}

####### PROJECT IDENTITY

c['title'] = config.APP_NAME
c['titleURL'] = ""

c['buildbotURL'] = "{}:{}/".format(config.BUILDBOT_HOST, config.BUILDBOT_PORT)

####### DB URL

c['db'] = {
    'db_url' : "sqlite:///state.sqlite",
}

####### BUILDSLAVES

from buildbot.buildslave import BuildSlave
c['slaves'] = [BuildSlave(config.SLAVE_NAME,
    config.SLAVE_PSW)]

c['protocols'] = {'pb': {'port': 9989}}

####### CHANGESOURCES

from buildbot.changes.gitpoller import GitPoller
c['change_source'] = []
c['change_source'].append(GitPoller(
        config.REPOSITORY,
        workdir='gitpoller-workdir',
        branches=True,
        pollinterval=5))

####### SCHEDULERS

from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.changes import filter
from buildbot.schedulers import timed

c['schedulers'] = []

c['schedulers'].append(SingleBranchScheduler(
                            name="release",
                            change_filter=filter.ChangeFilter(branch='master'),
                            treeStableTimer=None,
                            builderNames=['release']))

c['schedulers'].append(SingleBranchScheduler(
                            name="features",
                            change_filter=filter.ChangeFilter(branch_re = '.+'),
                            treeStableTimer=None,
                            builderNames=['continuously']))

c['schedulers'].append(ForceScheduler(
                            name="force",
                            builderNames=['nightly', 'weekly']))

c['schedulers'].append(timed.Nightly(name='sch_nightly',
    branch='develop',
    builderNames=['nightly'],
    hour=config.NIGHTLY_TIME[0],
    minute=config.NIGHTLY_TIME[1],
    onlyIfChanged=True))

c['schedulers'].append(timed.Nightly(name='sch_weekly',
    branch='develop',
    builderNames=['weekly'],
    dayOfWeek=config.WEEKLY_TIME[2],
    hour=config.WEEKLY_TIME[0],
    minute=config.WEEKLY_TIME[1],
    onlyIfChanged=True))

####### BUILDERS

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.steps import shell
from time import gmtime, strftime
from buildbot.process.properties import WithProperties, Interpolate

git_fetch_step = Git(
    repourl=config.REPOSITORY,
    mode='incremental',
    submodules=True,
    timeout=120)

export_sdk_cmd = 'export ANDROID_HOME={};'.format(config.ANDROID_HOME)
export_sdk_step = ShellCommand(command=export_sdk_cmd)
make_step = ShellCommand(command=export_sdk_cmd+config.PRE_MAKE_STEP+config.MAKE_STEP)
test_step = ShellCommand(command=export_sdk_cmd+config.TEST_STEP)

update_rev_step = shell.SetProperty(command='git rev-parse HEAD', property='gitlastrev')
update_tag_step = shell.SetProperty(command='git describe --tags | awk -F\'-\' \'{print $1}\'',
    property='gitversion')

def get_release_step(type):
    new_build_path = '../../../builds/{}_%(prop:gitversion)s_{}_{}.apk'.format(config.APP_NAME,
        type, strftime('%Y%m%d', gmtime()))

    return ShellCommand(command=[ 'cp', config.BUILD_LOCATION,
                                 Interpolate(new_build_path)])

def get_changelog_step(type):
    build_apk = '{}_%(prop:gitversion)s_{}_{}.apk'.format(config.APP_NAME,
        type, strftime('%Y%m%d', gmtime()))
    command_init = 'echo "" > ../../../changes/{}changes.log;'.format(type)
    command_add_return = 'echo "" >> ../../../changes/{}changes.log;'.format(type)
    changelog_cmd = command_init
    if type != 'continuously':
        changelog_cmd += 'echo "BUILD: {}:{}/{}" >> ../../../changes/{}changes.log;'.format(config.BUILDBOT_HOST,
            config.BUILDSLIST_PORT, build_apk, type)
        changelog_cmd += command_add_return
    else:
        changelog_cmd += 'echo "BRANCH: $(git branch | sed -e \'s/^* //\')" >> ../../../changes/{}changes.log;'.format(type)
        changelog_cmd += command_add_return
    return ShellCommand(command=Interpolate(changelog_cmd))


from buildbot.config import BuilderConfig
c['builders'] = []

### CONTINOUSLY ###

factory_continuously = BuildFactory()

factory_continuously.addStep(update_rev_step)
factory_continuously.addStep(git_fetch_step)
factory_continuously.addStep(export_sdk_step)
factory_continuously.addStep(test_step)
factory_continuously.addStep(get_changelog_step('continuously'))

c['builders'].append(
    BuilderConfig(name="continuously",
      slavenames=[config.SLAVE_NAME],
      factory=factory_continuously))

### NIGHTLY ###

factory_nightly = BuildFactory()

factory_nightly.addStep(update_rev_step)
factory_nightly.addStep(git_fetch_step)
factory_nightly.addStep(export_sdk_step)
factory_nightly.addStep(make_step)
factory_nightly.addStep(update_tag_step)
factory_nightly.addStep(get_release_step('nightly'))
factory_nightly.addStep(get_changelog_step('nightly'))


c['builders'].append(
    BuilderConfig(name="nightly",
      slavenames=[config.SLAVE_NAME],
      factory=factory_nightly))

### RELEASE ###

factory_release = BuildFactory()

factory_release.addStep(update_rev_step)
factory_release.addStep(git_fetch_step)
factory_release.addStep(export_sdk_step)
factory_release.addStep(make_step)
factory_release.addStep(update_tag_step)
factory_release.addStep(get_release_step('release'))
factory_release.addStep(get_changelog_step('release'))


c['builders'].append(
    BuilderConfig(name="release",
      slavenames=[config.SLAVE_NAME],
      factory=factory_release))

### WEEKLY ###

factory_weekly = BuildFactory()

factory_weekly.addStep(update_rev_step)
factory_weekly.addStep(git_fetch_step)
factory_weekly.addStep(export_sdk_step)
factory_weekly.addStep(make_step)
factory_weekly.addStep(update_tag_step)
factory_weekly.addStep(get_release_step('weekly'))
factory_weekly.addStep(get_changelog_step('weekly'))

c['builders'].append(
    BuilderConfig(name="weekly",
      slavenames=[config.SLAVE_NAME],
      factory=factory_weekly))

####### STATUS TARGETS

c['status'] = []

from buildbot.status import html
from buildbot.status.web import authz, auth

authz_cfg=authz.Authz(
    auth=auth.BasicAuth([(config.AUTH_USER, config.AUTH_PSW)]),
    gracefulShutdown = False,
    forceBuild = 'auth',
    forceAllBuilds = False,
    pingBuilder = False,
    stopBuild = False,
    stopAllBuilds = False,
    cancelPendingBuild = False,
)
c['status'].append(html.WebStatus(http_port=8010, authz=authz_cfg))

####### MAIL NOTIFIER

from buildbot.status.mail import MailNotifier
from buildbot.status.builder import Results

def messageFormatter(mode, name, build, results, master_status):
    result = Results[results]
    text = list()
    text.append("STATUS: %s" % result.title())
    if results == 0:
        text.append(open('../changes/{}changes.log'.format(name), 'r').read())
    build_url = 'Read more: {}:{}/builders/{}/builds/{}'.format(config.BUILDBOT_HOST, config.BUILDBOT_PORT,
        name, build.getNumber())
    text.append(build_url)

    return {
        'body' : '\n'.join(text),
        'subject' : '[{}!] {} {} {}'.format(result.title(), config.APP_NAME, name,
            strftime('%d-%m-%Y %H:%m:%S', gmtime())),
        'type' : 'plain'
    }

mn = MailNotifier(fromaddr=config.MAIL_USER,
                  sendToInterestedUsers=False,
                  extraRecipients=config.MAIL_RECIPIENTS,
                  useTls=config.MAIL_USE_TLS, relayhost=config.MAIL_SMTP_HOST,
                  smtpPort=config.MAIL_SMTP_PORT,
                  smtpUser=config.MAIL_USER,
                  smtpPassword=config.MAIL_PSW,
                  messageFormatter=messageFormatter)

c['status'].append(mn)

def get_additional_info(builderName, build, result):
    if result == 0:
        return open('../changes/{}changes.log'.format(builderName), 'r').read()
    else:
        return ''

for room in config.HIPCHAT_ROOMS:
    c['status'].append(hipchat.HipChatStatusPush(config.HIPCHAT_TOKEN, room,
        get_additional_info=get_additional_info))
