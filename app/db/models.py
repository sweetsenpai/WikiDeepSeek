from tortoise import fields, models


class WikiArticls(models.Model):
    """
    Модель статьи из Wikipedia
    """

    id = fields.IntField(primary_key=True)
    url = fields.CharField(max_length=512, index=True, unique=True)
    title = fields.CharField(max_length=200)
    text = fields.TextField()
    summary = fields.TextField()

    class Meta:
        table = 'wikiarticls'
