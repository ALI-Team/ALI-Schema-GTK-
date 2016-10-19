# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

import sys
import urllib2
import json
import time
import datetime

class ALISchemaWindow(Gtk.ApplicationWindow):

    def show_popover(self, button):
        if self.week_popover.get_visible():
            self.week_popover.hide()
        else:
            self.week_popover.show_all()

    def update_view(self, adjustment):
        self.week = str(self.week_picker.get_value_as_int())
        self.reload()


    def __init__(self, app):
        Gtk.Window.__init__(self, title="ALI-Schema", application=app)

        self.week = str(datetime.datetime.today().isocalendar()[1])

        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = "ALI-Schema"
        self.set_titlebar(self.header)

        self.week_button = Gtk.Button("v."+self.week)
        self.week_button.connect("clicked", self.show_popover)
        self.header.pack_start(self.week_button)

        grid = Gtk.Grid()

        self.week_adjustment = Gtk.Adjustment(int(self.week), 1, 52, 1, 10, 0)
        self.week_adjustment.connect("value-changed", self.update_view)

        self.week_picker = Gtk.SpinButton()
        self.week_picker.set_adjustment(self.week_adjustment)
        self.week_picker.set_range(1, 52)
        self.week_picker.set_value(int(self.week))

        label = Gtk.Label("Vecka")
        label.set_xalign(0  )

        grid.set_column_homogeneous(True)
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(self.week_picker, 1, 0, 1, 1)

        self.week_popover = Gtk.Popover()
        self.week_popover.set_position(Gtk.PositionType.BOTTOM)
        self.week_popover.set_relative_to(self.week_button)
        self.week_popover.set_border_width(5)
        self.week_popover.add(grid)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

    def reload(self):

        self.week_button.set_label("v."+self.week)

        days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]

        weeks = json.loads(urllib2.urlopen("http://jobb.matstoms.se/ali/api/getjson.php?week="+self.week+"&scid=89920&clid=na15c&getweek=1").read())

        for i in range(5):

            self.notebook.remove_page(i)

            list = Gtk.ListBox()
            list.set_selection_mode(Gtk.SelectionMode.NONE)

            for lesson in weeks["days"][i]["lessons"]:
                info = Gtk.Label(lesson["start"] + " - " + lesson["end"] + "\n" + lesson["info"])
                info.set_xalign(0)
                list.add(info)

            self.notebook.insert_page(list, Gtk.Label(days[i]), i)

        self.notebook.set_current_page(datetime.datetime.today().weekday())

        self.show_all()

class ALISchemaApplication(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = ALISchemaWindow(self)
        win.set_resizable(False)
        win.show_all()

        win.reload()

    def on_quit(self, action, param):
        self.quit()

    def show_settings(self, action, param):
        print("test")

    def do_startup(self):
        Gtk.Application.do_startup(self)

        builder = Gtk.Builder()
        builder.add_from_file("menus.ui")

        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.show_settings)
        self.add_action(settings_action)

        exit_action = Gio.SimpleAction.new("quit", None)
        exit_action.connect("activate", self.on_quit)
        self.add_action(exit_action)

        self.set_app_menu(builder.get_object("app-menu"))

app = ALISchemaApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
