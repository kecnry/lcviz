from traitlets import List, Unicode
from pathlib import Path

from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import (PluginTemplateMixin,
                                        DatasetSelectMixin, SelectPluginComponent)
from jdaviz.core.user_api import PluginUserApi

__all__ = ['ExportData']


@tray_registry('export-data', label="Export Data")
class ExportData(PluginTemplateMixin, DatasetSelectMixin):
    """
    See the :ref:`Export Data Plugin Documentation <export_data>` for more details.

    Only the following attributes and methods are available through the
    public plugin API.

    * ``dataset`` (:class:`~jdaviz.core.template_mixin.DatasetSelect`):
      Dataset to use for analysis.
    """
    template_file = __file__, "export_data.vue"

    format_items = List().tag(sync=True)
    format_selected = Unicode().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.format = SelectPluginComponent(self,
                                            items='format_items',
                                            selected='format_selected',
                                            manual_options=['ascii', 'csv', 'fits', 'hdf5', 'votable'])  # noqa


    @property
    def user_api(self):
        expose = ['dataset', 'format']
        return PluginUserApi(self, expose=expose)


    def save(self, filename=None, format=None):
        """
        Save the data with a provided filename or through an interactive save dialog.

        Parameters
        ----------
        filename : str or `None`
            Filename to autopopulate the save dialog.
        format : str
            Supported format string.  If `None`, will use ``format`` defined in plugin.
        """
        if filename is not None:
            filename = Path(filename).expanduser()

        if format is None:
            format = self.format.selected

        # create temporary file and serve to the browser's save dialog
        return filename, format


    def vue_save(self, *args, **kwargs):
        self.save()
