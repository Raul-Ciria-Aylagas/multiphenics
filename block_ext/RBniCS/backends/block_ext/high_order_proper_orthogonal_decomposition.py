# Copyright (C) 2016 by the block_ext authors
#
# This file is part of block_ext.
#
# block_ext is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# block_ext is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with block_ext. If not, see <http://www.gnu.org/licenses/>.
#

from block_ext import BlockFunctionSpace
from block_ext.RBniCS.backends.block_ext.matrix import Matrix
from RBniCS.backends.abstract import HighOrderProperOrthogonalDecomposition as AbstractHighOrderProperOrthogonalDecomposition
from RBniCS.backends.basic import ProperOrthogonalDecompositionBase as BasicHighOrderProperOrthogonalDecomposition
import block_ext.RBniCS.backends.block_ext
import block_ext.RBniCS.backends.block_ext.wrapping
from RBniCS.utils.decorators import BackendFor, Extends, override

HighOrderProperOrthogonalDecompositionBase = BasicHighOrderProperOrthogonalDecomposition(AbstractHighOrderProperOrthogonalDecomposition)

@Extends(HighOrderProperOrthogonalDecompositionBase)
@BackendFor("block_ext", inputs=(Matrix.Type(), BlockFunctionSpace))
class HighOrderProperOrthogonalDecomposition(HighOrderProperOrthogonalDecompositionBase):
    @override
    def __init__(self, V_or_Z):
        HighOrderProperOrthogonalDecompositionBase.__init__(self, V_or_Z, None, block_ext.RBniCS.backends.block_ext, block_ext.RBniCS.backends.block_ext.wrapping, block_ext.RBniCS.backends.block_ext.TensorSnapshotsList, block_ext.RBniCS.backends.block_ext.TensorBasisList)
        