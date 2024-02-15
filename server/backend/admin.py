from django.contrib import admin
from backend.models import BotUser, Vote, Voting, Channel, Information, File, Template
# Register your models here.


class VoteInline(admin.TabularInline):
    model = Vote

class FileInline(admin.TabularInline):
    model = File

@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    inlines = [VoteInline, FileInline]
    list_display = ['id']

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_id', 'full_name']

@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_id']

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['user', 'title']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'type']