#!/usr/bin/python2
# -*- coding: utf-8 -*-
# @File    : dictlook.py
# @Date    : 2018-03-15

from objc_util import ObjCClass, UIApplication, CGSize, on_main_thread
import sys, re, clipboard
import appex
import dialogs
import ui

UIReferenceLibraryViewController = ObjCClass('UIReferenceLibraryViewController')


@on_main_thread
def main():
    input_dict = None
    if len(sys.argv) >= 2 and sys.argv[1] == 'quick':
        if appex.is_running_extension() and re.search('http*:\/\/[^\s]+', appex.get_attachments()[0]) is None:
            input_dict = appex.get_attachments()[0]
        else:
            clip = re.search('^(?!http)+', clipboard.get())
            if clip != None:
                input_dict = clipboard.get()

    input = input_dict or dialogs.text_dialog()
    if input:
        referenceViewController = UIReferenceLibraryViewController.alloc().initWithTerm_(input)

        rootVC = UIApplication.sharedApplication().keyWindow().rootViewController()
        tabVC = rootVC.detailViewController()

        referenceViewController.setTitle_("Definition: '{}'".format(input))
        referenceViewController.setPreferredContentSize_(CGSize(540, 540))
        referenceViewController.setModalPresentationStyle_(2)

        # tabVC.addTabWithViewController_(referenceViewController)
        tabVC.presentViewController_animated_completion_(referenceViewController, True, None)


if __name__ == '__main__':
    main()
