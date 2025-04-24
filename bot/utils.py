from datetime import datetime
import pytz

# Константы для состояний ConversationHandler
INPUT_VACATION_START = 0
INPUT_VACATION_END = 1
INPUT_ARRIVAL_NOTIFICATION_TIME = 2
INPUT_DEPARTURE_NOTIFICATION_TIME = 3

# Часовой пояс Владивостока (используется только для определённых функций, если нужно)
VLADIVOSTOK_TZ = pytz.timezone('Asia/Vladivostok')