import os

from functools import cached_property
from glue.config import viewer_tool
from glue.core import HubListener
from glue.viewers.common.tool import Tool
from glue_jupyter.bqplot.common.tools import CheckableTool
from glue_jupyter.utils import debounced

from jdaviz.core.tools import SidebarShortcutPlotOptions
from lcviz.events import ViewerRenamedMessage


ICON_DIR = os.path.join(os.path.dirname(__file__), 'data', 'icons')

from jdaviz.core.tools import SidebarShortcutPlotOptions, SidebarShortcutExportPlot

ICON_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), 'data', 'icons'))

# point to the lcviz-version of plot options instead of jdaviz's
SidebarShortcutPlotOptions.plugin_name = 'lcviz-plot-options'
SidebarShortcutExportPlot.plugin_name = 'lcviz-export-plot'


__all__ = ['ViewerClone']


@viewer_tool
class ViewerClone(Tool):
    icon = os.path.join(ICON_DIR, 'viewer_clone')
    tool_id = 'lcviz:viewer_clone'
    action_text = 'Clone viewer'
    tool_tip = 'Clone this viewer'

    def activate(self):
        self.viewer.clone_viewer()


@viewer_tool
class EphemTool(CheckableTool, HubListener):
    icon = os.path.join(ICON_DIR, 'chart-timeline')
    tool_id = 'lcviz:ephem'
    action_text = 'Modify ephemeris for phase-folding'
    tool_tip = 'Interactively modify phase-folding (double-click to set position to 0.5 phase, alt/cmd+double-click to set t0 to 0.0 phase, drag to adjust period)'  # noqa

    def __init__(self, viewer, **kwargs):
        self._drag_start_pos = None
        self._drag_start_period = None
        super().__init__(viewer, **kwargs)

        self.viewer.session.hub.subscribe(self, ViewerRenamedMessage,
                                          handler=self._on_clear_ephem_component_cache)

    def activate(self):
        self.viewer.add_event_callback(self.on_set_phase0,
                                       events=['dblclick'])

        self.viewer.add_event_callback(self.on_drag,
                                       events=['dragstart', 'dragend', 'dragmove'])

    @cached_property
    def ephem_plugin(self):
        return self.viewer.jdaviz_helper.plugins.get('Ephemeris')

    @cached_property
    def ephem_component(self):
        return self.viewer.reference.split(':')[1]

    def _on_clear_ephem_component_cache(self, msg):
        if msg.new_viewer_ref != self.viewer.reference:
            return
        attr = 'ephem_component'
        if attr in self.__dict__:
            del self.__dict__[attr]

    @property
    def ephemeris(self):
        ephem_plugin = self.ephem_plugin
        if ephem_plugin is None:
            return {}
        return ephem_plugin.ephemerides.get(self.ephem_component, {})

    def deactivate(self):
        self.viewer.remove_event_callback(self.on_set_phase0)
        self.viewer.remove_event_callback(self.on_drag)

    def on_set_phase0(self, data):
        # data: {'event': 'dblclick',
        #        'pixel': {'x': 203.328125, 'y': 68},
        #        'domain': {'x': 0.5910159335365275, 'y': 0.9998664987573793},
        #        'button': 0,
        #        'altKey': False, 'ctrlKey': False, 'metaKey': False}
        phase_clicked = data['domain']['x']
        ephem_plugin = self.ephem_plugin
        if ephem_plugin is None:
            return
        ephemeris = self.ephemeris
        t0 = ephemeris.get('t0', 0)
        period = ephemeris.get('period', 1)
        target_phase = 0.0 if (data['altKey'] or data['metaKey']) else 0.5
        t0_new = t0+period*(phase_clicked-target_phase)
        self.ephem_plugin.update_ephemeris(self.ephem_component, t0=t0_new)

    @debounced(delay_seconds=0.05, method=True)
    def on_drag(self, data):
        if data['event'] == 'dragstart' or self._drag_start_pos is None or self._drag_start_period is None:
            self._drag_start_pos = data['domain']['x']
            self._drag_start_period = self.ephemeris.get('period', 1)
        elif data['event'] == 'dragend':
            self._drag_start_pos = None
            self._drag_start_period = None
        else:
            drag_new_pos = data['domain']['x']
            delta = drag_new_pos - self._drag_start_pos
            period_new = self._drag_start_period * (1 + delta/10)
            # TODO: needs throttling/debouncing
            self.ephem_plugin.update_ephemeris(self.ephem_component, period=period_new)
