from jdaviz.configs.specviz.plugins import UnitConversion
from jdaviz.core.registries import tray_registry

__all__ = ['UnitConversion']


@tray_registry('lcviz-unit-conversion', label="Unit Conversion")
class UnitConversion(UnitConversion):
    """
    See the :ref:`Unit Conversion Plugin Documentation <unit-conversion>` for more details.

    For a full list of exposed attributes, call ``dir(plugin)``.  Note that some attributes are
    applicable depending on the selection of ``viewer`` and/or ``layer``.  Below are
    a list of some common attributes and methods are available through the
    :ref:`public plugin API <plugin-apis>`:

    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.show`
    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.open_in_tray`
    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.close_in_tray`
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.docs_link = f"https://lcviz.readthedocs.io/en/{self.vdocs}/plugins.html#unit-conversion"
        self.docs_description = "Choose units for the time and flux axes."

    @property
    def spectrum_viewer(self):
        if hasattr(self, '_default_time_viewer_reference_name'):
            viewer_reference = self._default_time_viewer_reference_name
        else:
            viewer_reference = self.app._get_first_viewer_reference_name(
            )

        return self.app.get_viewer(viewer_reference)

    @property
    def user_api(self):
        api = super().user_api
        expose = [e for e in api._expose if e not in ('spectral_unit')]
        api._expose = expose

        return api
