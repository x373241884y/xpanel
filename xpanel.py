#!/bin/python -OO

VERSION = 0.1

BG_COLOR = "0xd6d6d6"
TASK_COLOR = "0x000000"
FOCUSED_COLOR = "0x1826de"
SHADED_COLOR = "0x808080"
MINIMIZED_COLOR = "0x808080"
LINE_COLOR = "0x606060"

TASK_SHADOW_COLOR = "0xffffff"
FOCUSED_SHADOW_COLOR = "0xffffff"
SHADED_SHADOW_COLOR = "0xffffff"
MINIMIZED_SHADOW_COLOR = "0xffffff"
DESKTOP_SHADOW_COLOR = "0xffffff"
CLOCK_SHADOW_COLOR = "0xffffff"

# ------------------------------------------------------------------------------
# Panel Spacing and Location Options: Measured in pixels
# ------------------------------------------------------------------------------
P_LOCATION = 1  # Panel placement: 0 = top, 1 = bottom
P_WIDTH = 0  # Panel width: 0 = Use full screen width
P_START = 0  # Starting X coordinate of the panel
P_SPACER = 12  # Spacing between panel objects
P_HEIGHT = 32  # Panel height

# ------------------------------------------------------------------------------
# Icon Size Options: Measured in pixels
# ------------------------------------------------------------------------------
APPL_I_HEIGHT = 32  # Application launcher icon height
APPL_I_WIDTH = 32  # Application launcher icon width

HIDDEN_SIZE = 2

FONT = "bitstream vera sans-8"

SHOWALL = 0

SHOWMINIMIZED = 0

ICON_LIST = {
    "default": "",
    "example": "/usr/share/imlib2/data/images/audio.png",
}

LAUNCHER = 1
LAUNCH_LIST = [
    ("xdotool key ctrl+alt+space", "/usr/share/icons/hicolor/24x24/apps/xfce4-panel-menu.png"),
    ("ToggleDesktop", "/usr/share/icons/Mist/24x24/places/user-desktop.png"),
    ("xfce4-terminal", "/usr/share/icons/gnome/32x32/apps/xfce-terminal.png"),
    ("firefox", "/usr/local/application/firefox/browser/chrome/icons/default/default32.png"),
    ("chromium-browser", "/usr/share/icons/hicolor/32x32/apps/chromium.png"),
    ("/home/toor/application/RubyMine-7.0.1/bin/rubymine.sh", "/home/toor/application/RubyMine-7.0.1/bin/rubymine.png"),
    ("/home/toor/application/android-studio/bin/studio.sh", "/home/toor/application/android-studio/bin/studio.png"),
    ("/usr/local/ide/pycharm-4.5.4/bin/pycharm.sh", "/usr/local/ide/pycharm-4.5.4/bin/pycharm.png"),
    ("/usr/local/ide/sublime_text_3/sublime_text", "/usr/local/ide/sublime_text_3/Icon/32x32/sublime-text.png"),
    ("/usr/bin/xfce4-terminal -e vimgui", "/usr/share/icons/hicolor/32x32/apps/gvim.png"),
    ("/usr/local/ide/idea-1415/bin/idea.sh", "/usr/local/ide/idea-1415/bin/idea.png"),
    ("/usr/local/ide/Aptana_Studio_3/AptanaStudio3", "/usr/local/ide/Aptana_Studio_3/aptana.png"),
    ("VirtualBox %U", "/usr/share/icons/hicolor/32x32/apps/virtualbox.png"),
    ("/home/toor/application/eclipse/eclipse", "/home/toor/application/eclipse/icon.xpm"),
    ("xpaint", "/usr/share/xpaint/xpaint.png"),
]

SHADE = 50

ABOVE = 1
APPICONS = 1
AUTOHIDE = 0
SHADOWS = 0
SHOWLINES = 1
SHOWBORDER = 1

P_START_X = 0
P_START_Y = 0


class Obj(object):
    # ----------------------------------------------------------------------------
    """ Multi-purpose class """
    # ----------------------------
    def __init__(self, **kwargs):
        # ----------------------------
        self.__dict__.update(kwargs)


# ----------------------------------------------------------------------------
class XPanel(object):
    # ----------------------------------------------------------------------------
    # ---------------------------
    def __init__(self, display):
        # ---------------------------
        """ Initialize and display the panel """
        self.display = display  # Display obj
        self.screen = display.screen()  # Screen obj
        self.root = self.screen.root  # Display root
        self.error = error.CatchError()  # Error Handler/Suppressor
        self.panel = {"sections": []}  # Panel data and layout
        self.colors = {}  # Alloc'd colors
        self.hidden = 0  # Panel hidden/minimized
        self.focus = 0  # Currently focused window
        self.rpm = None  # Root pixmap ID

        global P_HEIGHT, P_WIDTH, P_LOCATION

        # Misc. initializations
        if SHOWLINES or SHOWBORDER:
            self.lgc = self.root.create_gc(foreground=self.getColor(LINE_COLOR))
        if LAUNCH_LIST:
            P_WIDTH = len(LAUNCH_LIST) * (APPL_I_WIDTH + P_SPACER) - P_SPACER / 2

            P_START_X = (self.screen.width_in_pixels - P_WIDTH) / 2
            P_START_Y = self.screen.height_in_pixels - P_HEIGHT

            print "P_WIDTH:", P_WIDTH,",P_HEIGHT:",P_HEIGHT,",P_START_X:", P_START_X, ",P_START_Y:", P_START_Y
        if SHOWBORDER:
            P_HEIGHT += 2

        # Setup the panel's window
        self.window = self.screen.root.create_window(P_START_X, P_START_Y,
                                                     P_WIDTH, P_HEIGHT, 0, self.screen.root_depth,
                                                     window_class=X.InputOutput,
                                                     visual=X.CopyFromParent, colormap=X.CopyFromParent,
                                                     event_mask=(
                                                         X.ExposureMask | X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask | X.EnterWindowMask))
        ppinit(self.window.id, FONT)

        if LAUNCHER and LAUNCH_LIST:
            self.panel["sections"].append(LAUNCHER)
            self.panel[LAUNCHER] = Obj(id="launcher", tasks={}, order=[], first=0, last=0)
            self.createLauncher()

        # Init the properties and then start the event loop
        self.setProps(self.display, self.window)
        self.setStruts(self.window)
        self.root.change_attributes(event_mask=(X.PropertyChangeMask))
        self.window.map()
        self.display.flush()
        self.loop(self.display, self.root, self.window, self.panel)

    # ------------------------------------
    def clearPanel(self, x1, y1, x2, y2):
        # ------------------------------------
        """ Clear panel at the given coordinates """
        ppclear(self.window.id, int(x1), y1, int(x2), y2)
        if SHOWBORDER:
            self.window.rectangle(self.lgc, 0, 0, P_WIDTH - 1, P_HEIGHT - 1)

            # ------------------------

    def createLauncher(self):
        # ------------------------
        """ Initialize the Application Launcher """
        order = []
        tasks = {}
        for app, icon in LAUNCH_LIST:
            order.append(app)
            iobj = Obj(path=icon, data="", width=0, height=0, pixmap=0, mask=0)
            tasks[app] = Obj(x1=0, x2=0, app=app + " &", icon=iobj)
            self.panel[LAUNCHER].tasks = tasks
            self.panel[LAUNCHER].order = order
            # ---------------------------------

    def drawText(self, obj, x, width):
        # ---------------------------------
        """ Draw the given objects name at x """
        if SHADOWS:
            ppfont(self.window.id, obj.shadow, x + 1, P_HEIGHT + 2, width, obj.name)
        ppfont(self.window.id, obj.color, x, P_HEIGHT, width, obj.name)

    # ----------------------------------
    def setStruts(self, win, hidden=0):
        # ----------------------------------
        """ Set the panel struts according to the state (hidden/visible) """
        top = top_start = top_end = 0
        if not hidden:
            bottom = P_HEIGHT
        else:
            bottom = HIDDEN_SIZE

        bottom_start = P_START_X
        bottom_end = P_START_Y + P_WIDTH

        win.change_property(self._STRUT, Xatom.CARDINAL, 32, [0, 0, top, bottom])
        win.change_property(self._STRUTP, Xatom.CARDINAL, 32, [0, 0, top, bottom,
                                                               0, 0, 0, 0, top_start, top_end, bottom_start,
                                                               bottom_end])

    # ----------------------------
    def setProps(self, dsp, win):
        # ----------------------------
        """ Set necessary X atoms and panel window properties """
        self._ABOVE = dsp.intern_atom("_NET_WM_STATE_ABOVE")
        self._BELOW = dsp.intern_atom("_NET_WM_STATE_BELOW")
        self._BLACKBOX = dsp.intern_atom("_BLACKBOX_ATTRIBUTES")
        self._CHANGE_STATE = dsp.intern_atom("WM_CHANGE_STATE")
        self._CLIENT_LIST = dsp.intern_atom("_NET_CLIENT_LIST")
        self._CURRENT_DESKTOP = dsp.intern_atom("_NET_CURRENT_DESKTOP")
        self._DESKTOP = dsp.intern_atom("_NET_WM_DESKTOP")
        self._DESKTOP_COUNT = dsp.intern_atom("_NET_NUMBER_OF_DESKTOPS")
        self._DESKTOP_NAMES = dsp.intern_atom("_NET_DESKTOP_NAMES")
        self._HIDDEN = dsp.intern_atom("_NET_WM_STATE_HIDDEN")
        self._ICON = dsp.intern_atom("_NET_WM_ICON")
        self._NAME = dsp.intern_atom("_NET_WM_NAME")
        self._RPM = dsp.intern_atom("_XROOTPMAP_ID")
        self._SHADED = dsp.intern_atom("_NET_WM_STATE_SHADED")
        self._SHOWING_DESKTOP = dsp.intern_atom("_NET_SHOWING_DESKTOP")
        self._SKIP_PAGER = dsp.intern_atom("_NET_WM_STATE_SKIP_PAGER")
        self._SKIP_TASKBAR = dsp.intern_atom("_NET_WM_STATE_SKIP_TASKBAR")
        self._STATE = dsp.intern_atom("_NET_WM_STATE")
        self._STICKY = dsp.intern_atom("_NET_WM_STATE_STICKY")
        self._STRUT = dsp.intern_atom("_NET_WM_STRUT")
        self._STRUTP = dsp.intern_atom("_NET_WM_STRUT_PARTIAL")
        self._WMSTATE = dsp.intern_atom("WM_STATE")

        win.set_wm_name("XPanel")
        win.set_wm_class("XPanel", "XPanel")
        win.set_wm_hints(flags=(Xutil.InputHint | Xutil.StateHint),
                         input=0, initial_state=1)
        win.set_wm_normal_hints(flags=(
            Xutil.PPosition | Xutil.PMaxSize | Xutil.PMinSize),
            min_width=P_WIDTH, min_height=P_HEIGHT,
            max_width=P_WIDTH, max_height=P_HEIGHT)
        win.change_property(dsp.intern_atom("_WIN_STATE"), Xatom.CARDINAL, 32, [1])
        win.change_property(dsp.intern_atom("_MOTIF_WM_HINTS"),
                            dsp.intern_atom("_MOTIF_WM_HINTS"), 32, [0x2, 0x0, 0x0, 0x0, 0x0])
        win.change_property(self._DESKTOP, Xatom.CARDINAL, 32, [0xffffffffL])
        win.change_property(dsp.intern_atom("_NET_WM_WINDOW_TYPE"),
                            Xatom.ATOM, 32, [dsp.intern_atom("_NET_WM_WINDOW_TYPE_DOCK")])

    # --------------------------------------
    def getIcon(self, task, x, launcher=0):
        # --------------------------------------
        """ Get the icon from the given task and draw it at x """
        if not launcher and not APPICONS:
            return 0

        y = (P_HEIGHT - APPL_I_HEIGHT) / 2
        w = APPL_I_WIDTH
        h = APPL_I_HEIGHT
        name = task.app

        icon = task.icon
        # create icon in panel
        rc = ppicon(self.window.id, icon.pixmap, icon.mask, x, y, icon.width,
                    icon.height, w, h, icon.data, icon.path)
        if not rc:
            self.clearPanel(x, 0, w, P_HEIGHT)
            sys.stderr.write("Failed to get icon for '%s'\n%s\n\n" % (name, icon.path))

        return 1

    # -------------------------------
    def getColor(self, color):
        # -------------------------
        """ Function to get/convert/alloc a color given a single hex str """
        if color in self.colors:
            return self.colors[color]
        else:
            r = int("0x" + color[2:4], 0) * 257
            g = int("0x" + color[4:6], 0) * 257
            b = int("0x" + color[6:8], 0) * 257
            c = self.screen.default_colormap.alloc_color(r, g, b)

            if not c:
                sys.stderr.write("Error allocating color: %s\n" % color)
                return self.screen.white_pixel
            else:
                self.colors[color] = c.pixel
                return c.pixel

    def sendEvent(self, win, ctype, data, mask=None):
        # ------------------------------------------------
        """ Send a ClientMessage event to the root """
        data = (data + [0] * (5 - len(data)))[:5]
        ev = Xlib.protocol.event.ClientMessage(window=win, client_type=ctype, data=(32, (data)))

        if not mask:
            mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
        self.root.send_event(ev, event_mask=mask)

    # ---------------------
    def showDesktop(self):
        # ---------------------
        """ Toggle between hiding and unhiding ALL applications """
        showing = self.root.get_full_property(self._SHOWING_DESKTOP, 0)

        if hasattr(showing, "value"):
            if showing.value[0] == 0:
                self.sendEvent(self.root, self._SHOWING_DESKTOP, [1])
            else:
                self.sendEvent(self.root, self._SHOWING_DESKTOP, [0])


    def buttonRelease(self, root, panel, e):
        # ---------------------------------------
        """ Button Release event handler """
        x = e.event_x
        for section in panel["sections"]:
            if panel[section].id == "launcher" and e.detail == 1:
                for a in panel[section].tasks.values():
                    if x > a.x1 and x < a.x2:
                        if a.app.startswith("ToggleDesktop"):
                            self.showDesktop()
                            return
                        else:
                            os.system(a.app)
                            print 123
                            return
                            # -------------------------------------

    # focus in event
    def lanuchMouseMove(self, root, panel, e):
        x = e.event_x
        for a in panel[1].tasks.values():
            if x > a.x1 and x < a.x2:
                print a.app
                return

    # -------------------------------------
    def updateBackground(self, root, win):
        # -------------------------------------
        """ Check and update the panel background if necessary """
        rpm = root.get_full_property(self._RPM, Xatom.PIXMAP)

        if hasattr(rpm, "value"):
            rpm = rpm.value[0]
        else:
            rpm = root.id

        if self.rpm != rpm:
            self.rpm = rpm
            r = int("0x" + BG_COLOR[2:4], 0)
            g = int("0x" + BG_COLOR[4:6], 0)
            b = int("0x" + BG_COLOR[6:8], 0)
            ppshade(win.id, rpm, P_START_X, P_START_Y, P_WIDTH, P_HEIGHT, r, g, b, SHADE)

            # ---------------------------------------

    def updatePanel(self, root, win, panel):
        # ---------------------------------------
        """ Redraw the panel """
        curr_x = 0
        space = P_WIDTH
        launcher = None

        if LAUNCHER and panel[LAUNCHER].tasks:
            launcher = panel[LAUNCHER]
            space -= len(launcher.order) * APPL_I_WIDTH + 2

        # Clear the panel and add the objects
        self.updateBackground(root, win)
        self.clearPanel(0, 0, 0, 0)

        for section in panel["sections"]:

            if panel[section].id == "launcher" and launcher:
                curr_x += 2
                for app in launcher.order:
                    a = launcher.tasks[app]
                    a.x1 = curr_x
                    if self.getIcon(a, curr_x, 1):
                        curr_x += APPL_I_WIDTH + P_SPACER
                    a.x2 = curr_x
                curr_x += 1
                if SHOWLINES and not launcher.last:
                    win.poly_segment(self.lgc, [(curr_x, 0, curr_x, P_HEIGHT)])

                    # ------------------------------------------------------

    def updateTasks(self, dsp, root, win, panel, update=0):

        if update:
            self.updatePanel(root, win, panel)

            # -------------------------------------

    def loop(self, dsp, root, win, panel):
        focus = dsp.get_input_focus().focus

        if hasattr(focus, "id"):
            self.focus = focus.id

        while 1:
            while dsp.pending_events():
                e = dsp.next_event()
                if e.type == X.ButtonRelease:
                    self.buttonRelease(root, panel, e)
                elif e.type == X.DestroyNotify:
                    if self.taskDelete(e.window.id, panel):
                        self.updatePanel(root, win, panel)
                elif e.type == X.PropertyNotify:
                    if e.atom in [self._DESKTOP_NAMES, self._DESKTOP_COUNT]:
                        self.updatePanel(root, win, panel)
                    elif e.atom == self._RPM:
                        self.updatePanel(root, win, panel)

                elif e.type == X.EnterNotify and self.hidden:
                    if e.window.id == win.id:
                        self.updateTasks(dsp, root, win, panel)

                elif e.type == X.MotionNotify:
                    self.lanuchMouseMove(root, panel, e)

                elif e.type == X.Expose and e.count == 0:
                    if e.width == P_WIDTH:
                        win.change_property(self._DESKTOP, Xatom.CARDINAL, 32, [0xffffffffL])
                        self.sendEvent(win, self._STATE, [1, self._STICKY])
                        self.sendEvent(win, self._STATE, [1, self._SKIP_PAGER])
                        self.sendEvent(win, self._STATE, [1, self._SKIP_TASKBAR])
                        if ABOVE:
                            self.sendEvent(win, self._STATE, [1, self._ABOVE])
                        else:
                            self.sendEvent(win, self._STATE, [1, self._BELOW])
                        self.updateTasks(dsp, root, win, panel, 1)
                    else:
                        self.updatePanel(root, win, panel)

            rs, ws, es = select.select([dsp.display.socket], [], [], 20)


# ----------------------------------------------------------------------------
#                                  Main
# ----------------------------------------------------------------------------
from distutils import sysconfig
from Xlib import X, display, error, Xatom, Xutil
import Xlib.protocol.event
import locale, os, pwd, select, sys, time
from ppmodule import ppinit, ppshade, ppicon, ppfont, ppclear

if __name__ == "__main__":
    XPanel(display.Display())
