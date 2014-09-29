# Volatility
#
# Authors:
# Mike Auty <mike.auty@gmail.com>
#
# This file is part of Volatility.
#
# Volatility is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Volatility is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Volatility.  If not, see <http://www.gnu.org/licenses/>.
#

#pylint: disable-msg=C0111
from volatility import renderers
import volatility.plugins.common as common
import volatility.cache as cache
from volatility.renderers.basic import Address, Hex
import volatility.win32 as win32
import volatility.utils as utils

class Modules(common.AbstractWindowsCommand):
    """Print list of loaded modules"""
    def __init__(self, config, *args, **kwargs):
        common.AbstractWindowsCommand.__init__(self, config, *args, **kwargs)
        config.add_option("PHYSICAL-OFFSET", short_option = 'P', default = False,
                          cache_invalidator = False, help = "Physical Offset", action = "store_true")

    def unified_output(self, data):
        offsettype = "(V)" if not self._config.PHYSICAL_OFFSET else "(P)"
        tg = renderers.TreeGrid(
                          [("Offset{0}".format(offsettype), Address),
                           ("Name", str),
                           ('Base', Address),
                           ('Size', Hex),
                           ('File', str)
                           ])

        for module in data:
            if not self._config.PHYSICAL_OFFSET:
                offset = module.obj_offset
            else:
                offset = module.obj_vm.vtop(module.obj_offset)
            tg.append(None,
                      [Address(offset),
                       str(module.BaseDllName  or ''),
                       Address(module.DllBase),
                       Hex(module.SizeOfImage),
                       str(module.FullDllName or '')])
        return tg


    @cache.CacheDecorator("tests/lsmod")
    def calculate(self):
        addr_space = utils.load_as(self._config)

        result = win32.modules.lsmod(addr_space)

        return result

class UnloadedModules(common.AbstractWindowsCommand):
    """Print list of unloaded modules"""

    def unified_output(self, data):

        tg = renderers.TreeGrid([("Name", str),
                                 ('StartAddress', Address),
                                 ('EndAddress', Address),
                                 ('Time', str)])

        for drv in data:
            tg.append(None, [str(drv.Name),
                             Address(drv.StartAddress),
                             Address(drv.EndAddress),
                             str(drv.CurrentTime)])
        return tg

    def calculate(self):
        addr_space = utils.load_as(self._config)

        kdbg = win32.tasks.get_kdbg(addr_space)

        for drv in kdbg.MmUnloadedDrivers.dereference().dereference():
            yield drv
