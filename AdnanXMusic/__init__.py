from AdnanXMusic.core.bot import Adnany
from AdnanXMusic.core.dir import dirr
from AdnanXMusic.core.git import git
from AdnanXMusic.core.userbot import Userbot
from AdnanXMusic.misc import dbb, heroku
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Adnany()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()