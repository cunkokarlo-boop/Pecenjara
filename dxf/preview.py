import sys, glob, os, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
files = sorted(glob.glob(os.path.join(sys.argv[1], '*.dxf')))
fig, axs = plt.subplots(4, 3, figsize=(15, 18))
for ax in axs.flat: ax.axis('off')
for ax, f in zip(axs.flat, files):
    doc = ezdxf.readfile(f)
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace())
    ax.set_title(os.path.basename(f).replace('.dxf', ''), fontsize=9); ax.set_aspect('equal')
fig.patch.set_facecolor('white')
plt.tight_layout(); plt.savefig(sys.argv[2], dpi=110, facecolor='white')
