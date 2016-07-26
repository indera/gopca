from __future__ import (absolute_import, division,
                        print_function)
from builtins import str as text

import pkg_resources

from .params import GOPCAParams
from .signature import GOPCASignature
from .signature_matrix import GOPCASignatureMatrix
from .run import GOPCARun
from .go_pca import GOPCA

version = text(pkg_resources.require('gopca')[0].version)

__all__ = ['GOPCAParams', 'GOPCA', 'GOPCARun',
           'GOPCASignatureMatrix', 'GOPCASignature']
