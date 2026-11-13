import sys, math, numpy as np, bpy
from PIL import Image
sys.path.insert(0, '.')
import render7 as r7, camadas as c
def render_frente(i, out, d='v8out_deitado'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48
    sc.render.resolution_x, sc.render.resolution_y = 700, 660
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (1, 1, 1, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    preto, branco = r7.mat('p', (0.02, 0.02, 0.022), 0.4), r7.mat('b', (0.9, 0.9, 0.9), 0.5)
    M = np.array([[1,0,0,0],[0,0,-1,7],[0,1,0,25],[0,0,0,1]], float)
    import glob
    for k, m in (('preto', preto), ('branco', branco)):
        f = glob.glob(f'{d}/trofeu-{i}-*-{k}.stl')
        if f: r7.add(f[0], M, m)
    r7.add(f'{r7.BASE}/base-preto.stl', None, preto); r7.add(f'{r7.BASE}/base-branco.stl', None, branco)
    cam = bpy.data.cameras.new('c'); cam.type = 'ORTHO'; cam.ortho_scale = 350*c.S; cam.clip_end = 5000
    co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co
    el = math.radians(8); zc = 25 + (300-330/2)*c.S
    co.location = (0, -600*math.cos(el), zc + 600*math.sin(el)); co.rotation_euler = (math.pi/2 - el, 0, 0)
    for loc, en in (((-300, -400, 400), 600000), ((350, -250, 150), 200000), ((0, 300, 300), 150000)):
        l = bpy.data.lights.new('l', 'AREA'); l.energy = en; l.size = 300
        lo = bpy.data.objects.new('l', l); sc.collection.objects.link(lo); lo.location = loc
        a = bpy.data.objects.new('a', None); sc.collection.objects.link(a); a.location = (0, 0, 70)
        cc = lo.constraints.new('TRACK_TO'); cc.target = a; cc.track_axis = 'TRACK_NEGATIVE_Z'; cc.up_axis = 'UP_Y'
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)
if __name__ == '__main__':
    for i in [int(a) for a in sys.argv[1:]] or range(1, 10):
        render_frente(i, f'f_{i}.png')
        cx, ap = c.CX[i], c.APOIO[i]
        ref = Image.fromarray(c.REF[ap-300:ap+30, cx-175:cx+175].astype(np.uint8)).convert('RGB').resize((700, 660))
        s = Image.new('RGB', (1400, 660), 'white'); s.paste(ref, (0, 0)); s.paste(Image.open(f'f_{i}.png').convert('RGB'), (700, 0))
        s.save(f'lado_{i}.png')
