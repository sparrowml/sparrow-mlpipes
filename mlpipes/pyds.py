from typing import Generator, Union

import pyds


def pyds_generator(
    pyds_list: pyds.GList,
) -> Generator[Union[pyds.NvDsFrameMeta, pyds.NvDsObjectMeta], None, None]:
    """Create a generator of frame/object meta instances"""
    if pyds_list is None:
        return
    yield pyds_list
    while pyds_list:
        pyds_list = pyds_list.next
        if pyds_list is None:
            return
        yield pyds_list
