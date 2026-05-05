from cpm.m04_transformer.base import BaseBrowserAdapter
from cpm.m04_transformer.adapters.chrome import ChromiumBookmarksMixin


class CocCocAdapter(ChromiumBookmarksMixin, BaseBrowserAdapter):
    @property
    def browser_id(self) -> str:
        return "coccoc"
