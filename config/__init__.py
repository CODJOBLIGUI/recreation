"""Package marker for config."""


# Safe-guard for template context flattening.
# Prevents ValueError if a non-dict slips into Context.dicts (seen with Unfold).
try:
    from django.template.context import Context

    def _safe_flatten(self):
        flat = {}
        for d in self.dicts:
            if isinstance(d, dict):
                flat.update(d)
            else:
                try:
                    flat.update(dict(d))
                except Exception:
                    # Ignore invalid context entries instead of crashing.
                    continue
        return flat

    Context.flatten = _safe_flatten
except Exception:
    # If Django isn't ready yet, or import fails, do nothing.
    pass

