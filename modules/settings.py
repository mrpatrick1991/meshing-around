# Settings for MeshBot and PongBot
# 2024 Kelly Keeton K7MHI
import configparser

# messages
NO_DATA_NOGPS = "No location data: does your device have GPS?"
ERROR_FETCHING_DATA = "error fetching data"
WELCOME_MSG = 'MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, cmd? for more'
MOTD = 'Thanks for using MeshBOT! Have a good day!'
NO_ALERTS = "No weather alerts found."

# setup the global variables
MESSAGE_CHUNK_SIZE = 160 # message chunk size for sending at high success rate
SITREP_NODE_COUNT = 3 # number of nodes to report in the sitrep
msg_history = [] # message history for the store and forward feature
bbs_ban_list = [] # list of banned users, imported from config
bbs_admin_list = [] # list of admin users, imported from config
repeater_channels = [] # list of channels to listen on for repeater mode, imported from config
antiSpam = True # anti-spam feature to prevent flooding public channel
ping_enabled = True # ping feature to respond to pings, ack's etc.
sitrep_enabled = True # sitrep feature to respond to sitreps
lastHamLibAlert = 0 # last alert from hamlib
max_retry_count1 = 4 # max retry count for interface 1
max_retry_count2 = 4 # max retry count for interface 2
retry_int1 = False
retry_int2 = False
scheduler_enabled = False # enable the scheduler currently config via code only
wiki_return_limit = 3 # limit the number of sentences returned off the first paragraph first hit
llmRunCounter = 0
llmTotalRuntime = []

# Read the config file, if it does not exist, create basic config file
config = configparser.ConfigParser() 
config_file = "config.ini"

try:
    config.read(config_file)
except Exception as e:
    print(f"System: Error reading config file: {e}")

if config.sections() == []:
    print(f"System: Error reading config file: {config_file} is empty or does not exist.")
    config['interface'] = {'type': 'serial', 'port': "/dev/ttyACM0", 'hostname': '', 'mac': ''}
    config['general'] = {'respond_by_dm_only': 'True', 'defaultChannel': '0', 'motd': MOTD,
                         'welcome_message': WELCOME_MSG, 'zuluTime': 'False'}
    config.write(open(config_file, 'w'))
    print (f"System: Config file created, check {config_file} or review the config.template")

if 'sentry' not in config:
        config['Sentry'] = {'SentryEnabled': 'False', 'SentryChannel': '2', 'SentryHoldoff': '9', 'sentryIgnoreList': '', 'SentryRadius': '100'}
        config.write(open(config_file, 'w'))

if 'location' not in config:
        config['location'] = {'enabled': 'True', 'lat': '48.50', 'lon': '-123.0', 'UseMeteoWxAPI': 'False', 'useMetric': 'False', 'NOAAforecastDuration': '4', 'NOAAalertCount': '2', 'NOAAalertsEnabled': 'True'}
        config.write(open(config_file, 'w'))

if 'bbs' not in config:
        config['bbs'] = {'enabled': 'False', 'bbsdb': 'bbsdb.pkl', 'bbs_ban_list': '', 'bbs_admin_list': ''}
        config.write(open(config_file, 'w'))

if 'repeater' not in config:
        config['repeater'] = {'enabled': 'False', 'repeater_channels': ''}
        config.write(open(config_file, 'w'))

if 'radioMon' not in config:
        config['radioMon'] = {'enabled': 'False', 'rigControlServerAddress': 'localhost:4532', 'sigWatchBrodcastCh': '2', 'signalDetectionThreshold': '-10', 'signalHoldTime': '10', 'signalCooldown': '5', 'signalCycleLimit': '5'}
        config.write(open(config_file, 'w'))

# interface1 settings
interface1_type = config['interface'].get('type', 'serial')
port1 = config['interface'].get('port', '')
hostname1 = config['interface'].get('hostname', '')
mac1 = config['interface'].get('mac', '')

# interface2 settings
if 'interface2' in config:
    interface2_type = config['interface2'].get('type', 'serial')
    port2 = config['interface2'].get('port', '')
    hostname2 = config['interface2'].get('hostname', '')
    mac2 = config['interface2'].get('mac', '')
    interface2_enabled = config['interface2'].getboolean('enabled', False)
else:
    interface2_enabled = False

# variables
try:
    useDMForResponse = config['general'].getboolean('respond_by_dm_only', True)
    publicChannel = config['general'].getint('defaultChannel', 0) # the meshtastic public channel
    zuluTime = config['general'].getboolean('zuluTime', False) # aka 24 hour time
    log_messages_to_file = config['general'].getboolean('LogMessagesToFile', True) # default True
    syslog_to_file = config['general'].getboolean('SyslogToFile', False)
    urlTimeoutSeconds = config['general'].getint('urlTimeout', 10) # default 10 seconds
    store_forward_enabled = config['general'].getboolean('StoreForward', True)
    storeFlimit = config['general'].getint('StoreLimit', 3) # default 3 messages for S&F
    welcome_message = config['general'].get(f'welcome_message', WELCOME_MSG)
    welcome_message = (f"{welcome_message}").replace('\\n', '\n') # allow for newlines in the welcome message
    motd_enabled = config['general'].getboolean('motdEnabled', True)
    dad_jokes_enabled = config['general'].getboolean('DadJokes', False)
    solar_conditions_enabled = config['general'].getboolean('spaceWeather', True)
    wikipedia_enabled = config['general'].getboolean('wikipedia', False)
    llm_enabled = config['general'].getboolean('ollama', False) # https://ollama.com
    llmModel = config['general'].get('ollamaModel', 'gemma2:2b') # default gemma2:2b

    sentry_enabled = config['sentry'].getboolean('SentryEnabled', False) # default False
    secure_channel = config['sentry'].getint('SentryChannel', 2) # default 2
    sentry_holdoff = config['sentry'].getint('SentryHoldoff', 9) # default 9
    sentryIgnoreList = config['sentry'].get('sentryIgnoreList', '').split(',')
    sentry_radius = config['sentry'].getint('SentryRadius', 100) # default 100 meters

    location_enabled = config['location'].getboolean('enabled', True)
    latitudeValue = config['location'].getfloat('lat', 48.50)
    longitudeValue = config['location'].getfloat('lon', -123.0)
    use_meteo_wxApi = config['location'].getboolean('UseMeteoWxAPI', False) # default False use NOAA
    use_metric = config['location'].getboolean('useMetric', False) # default Imperial units
    forecastDuration = config['location'].getint('NOAAforecastDuration', 4) # NOAA forcast days
    numWxAlerts = config['location'].getint('NOAAalertCount', 2) # default 2 alerts
    wxAlertsEnabled = config['location'].getboolean('NOAAalertsEnabled', True) # default True not enabled yet
   
    bbs_enabled = config['bbs'].getboolean('enabled', False)
    bbsdb = config['bbs'].get('bbsdb', 'bbsdb.pkl')
    bbs_ban_list = config['bbs'].get('bbs_ban_list', '').split(',')
    bbs_admin_list = config['bbs'].get('bbs_admin_list', '').split(',')

    repeater_enabled = config['repeater'].getboolean('enabled', False)
    repeater_channels = config['repeater'].get('repeater_channels', '').split(',')

    radio_detection_enabled = config['radioMon'].getboolean('enabled', False)
    rigControlServerAddress = config['radioMon'].get('rigControlServerAddress', 'localhost:4532') # default localhost:4532
    sigWatchBroadcastCh = config['radioMon'].get('sigWatchBroadcastCh', '2').split(',') # default Channel 2
    signalDetectionThreshold = config['radioMon'].getint('signalDetectionThreshold', -10) # default -10 dBm
    signalHoldTime = config['radioMon'].getint('signalHoldTime', 10) # default 10 seconds
    signalCooldown = config['radioMon'].getint('signalCooldown', 5) # default 1 second
    signalCycleLimit = config['radioMon'].getint('signalCycleLimit', 5) # default 5 cycles, used with SIGNAL_COOLDOWN

except KeyError as e:
    print(f"System: Error reading config file: {e}")
    print(f"System: Check the config.ini against config.template file for missing sections or values.")
    print(f"System: Exiting...")
    exit(1)
