#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import common
import ui, clipboard, console
from utils import py_utils

_icons = py_utils.load_config(file='config/icon.json')


def create_swatch_image(icon, w=32):
    return ui.Image('iob:' + icon)


class MyDataClass(object):
    # supplies our list with records that are formatted for
    # ui.ListDataSource. Because we create swatch images, this is a good
    # idea. All the swatchs' are created once and kept.
    def __init__(self, *args, **kwargs):
        self.data = self._my_data(_icons)

    def _my_data(self, lst):
        # ListDataSource format
        return [{'title': clr,
                 'image': create_swatch_image(clr, w=24),
                 'accessory_type': 'detail_button'
                 } for i, clr in enumerate(sorted(lst))]

    def filter(self, filter=''):
        # return the data, if filter is not passed, all records returned
        # else a subset of records are returned based on the filter.
        return [d for d in self.data if filter in d['title']]


def make_ui_object(ui_type, *args, **kwargs):
    # utility to create ui object with all kwargs
    obj = ui_type()
    for k, v in kwargs.items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    return obj


class Panel(ui.View):
    # a base class, not doing much, can do more.
    def __init__(self, p, h, *args, **kwargs):
        '''
                p = the intended parent view
                h = the height of the panel
        '''
        # set the frame before calling super incase kwargs contridicts
        # the normal setup
        f = ui.Rect(0, 0, p.width, h)
        self.frame = f
        super().__init__(*args, **kwargs)
        self.default_action = None

        # add ourself to the parent...recalcitrant child
        # probably not good form to do this, not sure
        p.add_subview(self)


class SearchPanel(Panel):
    def __init__(self, p, h, *args, **kwargs):
        super().__init__(p, h, *args, **kwargs)
        self.name = 'sp'
        self.bg_color = '#99abb7'
        self.flex = 'wrb'

        self.make_view()

    def make_view(self):
        txtfld = make_ui_object(ui.TextField)
        txtfld.placeholder = 'Filter'
        txtfld.clear_button_mode = 'always'
        txtfld.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
        txtfld.spellchecking_type = False

        txtfld.frame = self.bounds.inset(8, 4)
        txtfld.delegate = self
        txtfld.flex = 'wrb'
        self.add_subview(txtfld)

    def textfield_did_change(self, textfield):
        # send the contents of search field to our default_action if
        # it has been set.
        if self.default_action:
            self.default_action(self, textfield.text)


class ListPanel(Panel):
    def __init__(self, p, h, *args, **kwargs):
        super().__init__(p, h, *args, **kwargs)
        self.name = 'lp'
        self.dc = MyDataClass()
        self.lds = None

        self.make_view()

    def make_view(self):
        tv = ui.TableView(name='lst', frame=self.bounds)
        lds = ui.ListDataSource(items=self.dc.data)
        lds.delete_enabled = False
        lds.action = self.action
        lds.accessory_action = self.accessory_action
        tv.data_source = lds

        tv.flex = 'whlrtb'
        tv.delegate = lds
        self.add_subview(tv)
        self.lds = lds

    def filter(self, text):
        '''
                filter the list, very crude...
        '''
        tb = self['lst']
        self.lds.items = self.dc.filter(text)
        tb.content_offset = (0, 0)

    @property
    def num_records(self):
        return len(self.lds.items)

    def accessory_action(self, sender):
        if self.default_action:
            item = sender.items[sender.tapped_accessory_row]
            self.default_action(self, item['title'])

    def action(self, sender):
        # maybe will use later. But dont want to use this to copy the
        # color to the clipboard.
        pass


class FooterPanel(Panel):
    '''
            for now, just shows a label with the number of items displayed
            in the list.
    '''

    def __init__(self, p, h, *args, **kwargs):
        super().__init__(p, h, *args, **kwargs)
        self.name = 'fp'
        self.make_view()
        self.bg_color = '#99abb7'
        self.flex = 'wlt'

    def make_view(self):
        lb = make_ui_object(ui.Label, name='msg_lb', frame=self.frame)
        lb.text_color = 'white'
        lb.font = ('Avenir Next Condensed', 22)
        lb.alignment = ui.ALIGN_CENTER
        lb.center = self.center
        lb.flex = 'wlt'
        self.add_subview(lb)

    @property
    def msg_text(self):
        return self['msg_lb'].text

    @msg_text.setter
    def msg_text(self, msg_text):
        self['msg_lb'].text = msg_text


class IconClass(ui.View):

    # the presentation class so to speak
    def __init__(self, callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.make_view()
        self.callback = callback

    def make_view(self):
        # create the views, only sized. Positioning happens in layout
        sp = SearchPanel(self, 44)
        lp = ListPanel(self, 300)
        fp = FooterPanel(self, 32)

        # set callbacks
        sp.default_action = self.cb_search_text
        lp.default_action = self.cb_info_button

        self['fp'].msg_text = 'Items - {}'.format(self['lp'].num_records)

    def layout(self):
        '''
                position the views.
                manually resize the height of the listpanel
                should do all this with flex, later...
        '''
        v = self['sp']
        v.y = 0

        v = self['fp']
        v.y = self.bounds.max_y - v.height

        v = self['lp']
        v.y = self['sp'].bounds.max_y
        v.height = self.height - (self['sp'].height + self['fp'].height)

    def cb_search_text(self, sender, text):
        # the searchpanel calling us with the text in the textfield
        self['lp'].filter(text.lower())
        self['fp'].msg_text = 'Items - {}'.format(self['lp'].num_records)

    def cb_info_button(self, sender, text):
        if self.callback != None:
            self.close()
            self.callback(text)
        else:
            # the listpanel calling us with the text from the ui.TableView
            quote = "'"
            clipboard.set('{quote}{item}{quote}'.format(item=text,
                                                        quote=quote))
            console.hud_alert(text + '-Copied')
        self.close()


if __name__ == '__main__':
    w = 380
    h = ui.get_screen_size()[1] * .6
    f = (0, 0, w, h)
    style = ''
    title_color = 'white'
    title_bar_color = '#99abb7'
    animated = False

    # just added this...
    if not style is 'sheet' and not style is 'panel':
        w, h = ui.get_screen_size()
        f = (0, 0, w, h)

    mc = IconClass(name='图标选择器', frame=f, bg_color='white')

    mc.present(style=style, animated=animated,
               title_color=title_color,
               title_bar_color=title_bar_color)
