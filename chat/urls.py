from django.urls import path, re_path
from chat.views import chat, new_message_check, wink, chat_ajax, chat_home, read_messages, winks, read_wink, read_view, views, reject

urlpatterns = [
    re_path(r'^(?P<id>\d+)', chat, name="chat"),
    path('home/', chat_home, name="chat_home"),
    path('ajax/winks/', wink, name="wink"),
    path('ajax/reject/', reject, name="reject"), 
    path('ajax/new_message_check/', new_message_check, name='new_message_check'),
    path('ajax/read/', read_messages, name="read_messages"),
    path('ajax/new_message/', chat_ajax, name="new_message"),
    path('winks/', winks, name="winks"),
    path('views/', views, name="views"),
    path('ajax/read-view/', read_view, name='read_view'),
    path('ajax/read-wink/', read_wink, name='read_wink'),
]