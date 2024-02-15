from django.db import models

# Create your models here.

class BotUser(models.Model):
    class Lang(models.TextChoices):
        UZ = 'uz'
        RU = 'ru'
        EN = 'en'

    chat_id = models.IntegerField(unique=True)
    full_name = models.CharField(max_length=255, verbose_name="To'liq ismi")
    lang = models.CharField(
        max_length=10,
        choices=Lang.choices,
        default=Lang.UZ
    )
    bot_state = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
    

class Channel(models.Model):
    user = models.ForeignKey(to=BotUser, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=255)
    chat_id=models.CharField(max_length=50)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Kanal'
        verbose_name_plural = 'Kanallar'


    
class Information(models.Model):
    user = models.ForeignKey(to=BotUser, related_name='users', on_delete=models.CASCADE)
    channel = models.ForeignKey(to=Channel, on_delete=models.SET_NULL, blank=True, null=True)
    body = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.body
    
class Vote(models.Model):
    information = models.ForeignKey(to=Information, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=200)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    

class File(models.Model):
    information = models.ForeignKey(to=Information, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    file_id = models.CharField(max_length=500)

    def __str__(self):
        return self.file_id
    
class Voting(models.Model):
    chat_id = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    information = models.ForeignKey(to=Information, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return f"User: {self.chat_id} {self.information.id} ga ovoz berdi "
    
    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Ovoz berish'
        verbose_name_plural = 'Ovoz berganlar'


class KeyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='Key')


class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='Message')


class SmileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='Smile')


class Template(models.Model):
    class Type(models.TextChoices):
        KEY = 'Key'
        MESSAGE = 'Message'
        SMILE = 'Smile'

    templates = models.Manager()
    keys = KeyManager()
    messages = MessageManager()
    smiles = SmileManager()

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=Type.choices)
    body_uz = models.TextField()
    body_ru = models.TextField()
    body_en = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)

        keys = Template.keys.all()
        messages = Template.messages.all()
        smiles = Template.smiles.all()
        with open('backend/templates.py', 'w') as file:
            file.write('from .models import Template\n\n')
            file.write('\n')
            file.write('keys = Template.keys.all()\n')
            file.write('messages = Template.messages.all()\n')
            file.write('smiles = Template.smiles.all()\n\n')
            file.write('\n')
            file.write('class Keys():\n')
            for index, key in enumerate(keys):
                file.write(f'    {key.title} = keys[{index}]\n')

            file.write('\n\n')
            file.write('class Messages():\n')
            for index, message in enumerate(messages):
                file.write(f'    {message.title} = messages[{index}]\n')

            file.write('\n\n')
            file.write('class Smiles():\n')
            for index, smile in enumerate(smiles):
                file.write(f'    {smile.title} = smiles[{index}]\n')

        return result

    @property
    def text(self):
        return self.body_uz

    def get(self, lang):
        return getattr(self, f'body_{lang}')

    def getall(self):
        return (self.body_uz, self.body_ru, self.body_en)

    def format(self, **kwargs):
        return self.body_uz.format(**kwargs)

    def __format__(self, format_spec):
        return format(self.body_uz, format_spec)

    def __str__(self):
        return self.title
