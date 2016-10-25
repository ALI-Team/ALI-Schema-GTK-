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

class ALISchemaSettingsWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Inställningar", application=app)

        self.set_resizable(False)
        self.set_border_width(10)

        grid = Gtk.Grid()

        skola_label = Gtk.Label("Skola")
        skola_label.set_xalign(0)

        klass_label = Gtk.Label("Klass, Personnummer, id...")
        klass_label.set_xalign(0)

        school_list = json.load(open("schools.json", "r"))

        school_store = Gtk.ListStore(str, str)

        for school in school_list:
            school_store.append([school["id"], school["namn"] + " ("+school["stad"]+")"])

        skola = Gtk.ComboBox(model=school_store)

        cell = Gtk.CellRendererText()

        skola.pack_start(cell, False)
        skola.add_attribute(cell, "text", 1)

        klass = Gtk.Entry()

        grid.set_column_homogeneous(True)
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)

        grid.attach(skola_label, 0, 0, 1, 1)
        grid.attach(skola, 1, 0, 1, 1)
        grid.attach(klass_label, 0, 1, 1, 1)
        grid.attach(klass, 1, 1, 1, 1)

        self.add(grid)

class ALISchemaWindow(Gtk.ApplicationWindow):

    def show_popover(self, button):
        if self.week_popover.get_visible():
            self.week_popover.hide()
        else:
            self.week_popover.show_all()

    def update_view(self, adjustment):
        self.week = str(self.week_picker.get_value_as_int())
        self.reload()

    def reset_week(self, button):
        self.week = str(datetime.datetime.today().isocalendar()[1])
        self.week_picker.set_value(int(self.week))
        self.reload()

    def callback(self, source_object, result, user_data):
        try:
            success, content, etag = source_object.load_contents_finish(result)
        except Glib.GError as e:
            print("error: " + e.message)
        else:

            print("Recieved data for page: "+str(user_data))

            days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]

            weeks = json.loads(content.decode("utf-8"))

            list = self.notebook.get_nth_page(user_data)

            for container in list.get_children():
                list.remove(container)

            for lesson in weeks["lessons"]:
                info = Gtk.Label(lesson["start"] + " - " + lesson["end"] + "\n" + lesson["info"])
                info.set_xalign(0)
                list.add(info)
                self.show_all()

    def day_changed(self, notebook, widget, page):

        print("Notebook changed page")

        self.week_button.set_label("v."+self.week)

        file = Gio.File.new_for_uri("http://jobb.matstoms.se/ali/api/getjson.php?week="+self.week+"&scid=89920&clid=na15c&getweek=0&day="+str(page+1)+"")
        file.load_contents_async(Gio.Cancellable(), self.callback, page)

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

        self.this_week = Gtk.Button("Denna vecka")
        self.this_week.connect("clicked", self.reset_week)

        label = Gtk.Label("Vecka")
        label.set_xalign(0)

        grid.set_row_spacing(5)
        grid.set_column_homogeneous(True)

        grid.attach(label, 0, 0, 1, 1)
        grid.attach(self.week_picker, 1, 0, 1, 1)
        grid.attach(self.this_week, 0, 2, 2, 2)

        self.week_popover = Gtk.Popover()
        self.week_popover.set_position(Gtk.PositionType.BOTTOM)
        self.week_popover.set_relative_to(self.week_button)
        self.week_popover.set_border_width(5)
        self.week_popover.add(grid)

        self.notebook = Gtk.Notebook()

        days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]

        for i in range(5):
             list = Gtk.ListBox()
             list.set_selection_mode(Gtk.SelectionMode.NONE)
             self.notebook.insert_page(list, Gtk.Label(days[i]), i)

        self.notebook.connect("switch-page", self.day_changed)

        self.add(self.notebook)

    def reload(self):

        print("asd")


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
        settings_window = ALISchemaSettingsWindow(self)
        settings_window.show_all()

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
