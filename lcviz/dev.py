from contextlib import contextmanager


__all__ = ['is_enabled']


class FeatureFlags:
    def __init__(self):
        self._enabled = {'tpf': False}

    def is_enabled(self, feature):
        return self._enabled.get(feature, False)

    def enable(self, *features):
        for feature in features:
            if feature not in self._enabled:
                continue
            self._enabled[feature] = True

    @contextmanager
    def temporarily_enabled(self, *features):
        enabled_orig = self._enabled.copy()
        self.enable(*features)
        yield
        self._enabled = enabled_orig


_enabled = FeatureFlags()


def is_enabled(feature):
    # check if a feature flag is currently enabled
    return _enabled.is_enabled(feature)


def enable(*features):
    # enable a feature flag for the remainder of the session
    _enabled.enable(*features)


@contextmanager
def temporarily_enabled(*features):
    # temporarily enable a feature flag (useful for tests)
    with _enabled.temporarily_enabled(*features):
        yield
