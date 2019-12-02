#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from objc_util import *

UILocalNotification = ObjCClass('UILocalNotification')
UIUserNotificationSettings = ObjCClass('UIUserNotificationSettings')
NSDate = ObjCClass('NSDate')
app = UIApplication.sharedApplication()


@on_main_thread
def authorize():
    types = ((1 << 0) | (1 << 1) | (1 << 2))
    settings = UIUserNotificationSettings.settingsForTypes_categories_(types, None)
    app.registerUserNotificationSettings_(settings)


@on_main_thread
def schedule(message, alertTitle='', delay=1, sound_name=None, action_url=None):
    n = UILocalNotification.alloc().init().autorelease()
    n.alertTitle = alertTitle
    n.fireDate = NSDate.dateWithTimeIntervalSinceNow_(delay)
    fire_date_since1970 = n.fireDate().timeIntervalSince1970()
    n.alertBody = message
    if action_url:
        n.userInfo = {'actionURL': action_url}
    if sound_name is not None:
        if ':' in sound_name:
            collection, filename = sound_name.split(':')
            sound_name = 'Media/Sounds/%s/%s' % (collection, filename)
        n.soundName = sound_name + '.caf'
    app.scheduleLocalNotification_(n)
    info = {'message': message, 'fire_date': fire_date_since1970, 'action_url': action_url or '',
            'sound_name': sound_name or ''}
    return info


@on_main_thread
def get_scheduled():
    scheduled = app.scheduledLocalNotifications()
    infos = []
    for n in scheduled:
        message = str(n.alertBody())
        since1970 = n.fireDate().timeIntervalSince1970()
        user_info = n.userInfo()
        action_url = user_info['actionURL']
        if action_url is None:
            action_url = ''
        sound_name = n.soundName()
        sound_name = str(sound_name) if sound_name else ''
        info = {'message': message, 'fire_date': since1970, 'action_url': action_url, 'sound_name': sound_name}
        infos.append(info)
    return infos


@on_main_thread
def cancel(notification):
    infos = get_scheduled()
    try:
        i = infos.index(notification)
        scheduled = app.scheduledLocalNotifications()
        cancel = scheduled[i]
        app.cancelLocalNotification_(cancel)
    except ValueError:
        pass


@on_main_thread
def cancel_all():
    app.cancelAllLocalNotifications()


authorize()
