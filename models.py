from datetime import datetime
from utils.database import db

class BitcoinData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    supply = db.Column(db.Float, nullable=False)
    max_supply = db.Column(db.Float, nullable=False)
    price_usd = db.Column(db.Float, nullable=False)
    market_cap_usd = db.Column(db.Float, nullable=False)
    change_percent_24hr = db.Column(db.Float, nullable=False)
    volume_usd_24hr = db.Column(db.Float, nullable=False)
    vwap_24hr = db.Column(db.Float, nullable=False)
    sentiment = db.Column(db.Float, nullable=False)
    explorer = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BitcoinData {self.price_usd}>"
