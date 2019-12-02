#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : 佚名
# @Date    : 2018-03-15
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun

import time

import appex
import ui
from objc_util import ObjCClass

NSUserDefaults = ObjCClass('NSUserDefaults')

_MY_UPDATE_KEY = 'com.phuket2.pythonista.widget.last_update_key'
_WIDGET_NAME = 'My Widget'


class TodayWidgetBase(ui.View):
    NAME = _WIDGET_NAME

    # Can be whatever, but it should be unique per Pythonista & any script
    # Reversed domain is used followed by whatever you want
    _LAST_UPDATE_KEY = _MY_UPDATE_KEY

    def __init__(self, update_interval=10, **kwargs):
        super().__init__(self, **kwargs)

        self.update_interval = update_interval
        self._defaults = None

        # WidgetView is being initialized, we should update content
        self.update_content(force=True)

    @property
    def defaults(self):
        if not self._defaults:
            self._defaults = NSUserDefaults.standardUserDefaults()
        return self._defaults

    @property
    def last_update(self):
        return self.defaults.integerForKey_(self._LAST_UPDATE_KEY)

    @last_update.setter
    def last_update(self, value):
        self.defaults.setInteger_forKey_(value, self._LAST_UPDATE_KEY)

    def update(self):
        self.update_content()

    def update_content(self, force=False):
        # Get the time of when the update was called
        #
        # NOTE: Casting to int, because setFloat_forKey_ and floatForKey_ on self.defaults
        #       produces weird values
        timestamp = int(time.time())

        if not force and timestamp - self.last_update < self.update_interval:
            # Not enough time elapsed and we're not forced (initialisation) to update content, just skip it
            return

        # Update content in whatever way
        self.update_widget()

        if not force:
            # If update wasn't forced
            self.update_widget()

        # Store the time, just for the next comparison
        self.last_update = timestamp


class MyTodayWidget(TodayWidgetBase):
    def __init__(self, update_interval=10, **kwargs):
        self.start_time = time.time()
        self.lb = None
        self.make_view()
        super().__init__(update_interval, **kwargs)

    def make_view(self):
        lb = ui.Label(frame=self.bounds,
                      flex='WH',
                      alignment=ui.ALIGN_CENTER)
        self.lb = lb
        self.add_subview(lb)

    def update_widget(self):
        self.lb.text = str(time.time() - self.start_time)

# just for testing...After code correct, _PREVIEW should be False so you can
# run your code to setup persitent data etc...
# _PREVIEW = True

# if not appex.is_running_extension() and not _PREVIEW:
#    print('here we can set up what we need to do, write to a database etc...')

# else:
#    # note if h <= 120 you will not see the 'show more' button in the menu bar
#    # at least thats what i can see!
#    f = (0, 0, 500, 220)
#    update_interval = 1
#    widget_view = appex.get_widget_view()
#    # Can't use isinstance(widget_view, TimestampWidgetView) here, just use .name property
#    if widget_view and widget_view.name == MyTodayWidget.NAME:
#        widget_view.update_content()
#    else:
#        widget_view = MyTodayWidget(update_interval, frame=f)
#        widget_view.name = MyTodayWidget.NAME
#        appex.set_widget_view(widget_view)
