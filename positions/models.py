from mongoengine import Document, fields


class Positions(Document):
    ad_id = fields.IntField(required=True)
    position = fields.StringField(required=True)
    place = fields.StringField()
    comment = fields.StringField(max_length=120)
