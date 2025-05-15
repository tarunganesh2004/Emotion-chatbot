from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class EmotionLog(Base):
    __tablename__ = 'emotion_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    emotion = Column(String)
    timestamp = Column(DateTime)

class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    user_message = Column(String)
    bot_response = Column(String)
    emotion = Column(String)
    timestamp = Column(DateTime)

class DBHandler:
    def __init__(self, db_path):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def log_emotion(self, user_id, emotion, timestamp):
        session = self.Session()
        try:
            log = EmotionLog(user_id=user_id, emotion=emotion, timestamp=timestamp)
            session.add(log)
            session.commit()
        # # Reference: https://medium.com/@pankajkumargupta/build-a-real-time-face-emotion-detection-system-with-python-opencv-and-deepface-a-step-by-step-d4c9370f769b
        except Exception as e:
            logger.error(f"Error logging emotion: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def log_chat(self, user_id, user_message, bot_response, emotion, timestamp):
        session = self.Session()
        try:
            log = ChatLog(user_id=user_id, user_message=user_message, bot_response=bot_response,
                         emotion=emotion, timestamp=timestamp)
            session.add(log)
            session.commit()
        except Exception as e:
            logger.error(f"Error logging chat: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def get_emotion_stats(self, user_id):
        session = self.Session()
        try:
            week_ago = datetime.now() - timedelta(days=7)
            stats = session.query(EmotionLog.emotion, func.count(EmotionLog.emotion))\
                          .filter(EmotionLog.user_id == user_id, EmotionLog.timestamp >= week_ago)\
                          .group_by(EmotionLog.emotion).all()
            total = sum(count for _, count in stats)
            if total == 0:
                return {'labels': [], 'data': []}
            labels, data = zip(*[(emotion, (count/total)*100) for emotion, count in stats])
            return {'labels': list(labels), 'data': list(data)}
        except Exception as e:
            logger.error(f"Error fetching emotion stats: {str(e)}")
            return {'labels': [], 'data': []}
        finally:
            session.close()