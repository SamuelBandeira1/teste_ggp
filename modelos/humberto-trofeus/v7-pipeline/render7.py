import sys, os, math, numpy as np, bpy, trimesh, glob
BASE = '../trofeus/base7_montado'
def mat(nome, cor, rough):
    m = bpy.data.materials.new(nome); m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']; bsdf.inputs['Base Color'].default_value = (*cor, 1); bsdf.inputs['Roughness'].default_value = rough
    return m
def add(path, M, material):
    t = trimesh.load(path)
    if M is not None: t.apply_transform(M)
    me = bpy.data.meshes.new(os.path.basename(path)); me.from_pydata(t.vertices.tolist(), [], t.faces.tolist()); me.update()
    for p in me.polygons: p.use_smooth = False
    ob = bpy.data.objects.new(me.name, me); bpy.context.scene.collection.objects.link(ob); ob.data.materials.append(material)
    return ob
def render(i, out, deitado_dir):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 64
    try: sc.cycles.use_denoising = True
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = 560, 700
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (1, 1, 1, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    preto, branco = mat('p', (0.025, 0.025, 0.028), 0.45), mat('b', (0.85, 0.85, 0.85), 0.5)
    # deitado -> em pé: X=x, Y=7-z, Z=y+25
    M = np.array([[1,0,0,0],[0,0,-1,7],[0,1,0,25],[0,0,0,1]], float)
    for k, m in (('preto', preto), ('branco', branco)):
        f = glob.glob(f'{deitado_dir}/trofeu-{i}-*-{k}.stl')
        if f: add(f[0], M, m)
    add(f'{BASE}/base-preto.stl', None, preto); add(f'{BASE}/base-branco.stl', None, branco)
    cam = bpy.data.cameras.new('c'); cam.lens = 85; cam.clip_start = 1; cam.clip_end = 5000
    co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co
    ang = math.radians(16); dist = 400
    co.location = (dist*math.sin(ang), -dist*math.cos(ang), 60 + dist*math.sin(math.radians(9)))
    alvo = bpy.data.objects.new('alvo', None); sc.collection.objects.link(alvo); alvo.location = (0, 0, 62)
    c = co.constraints.new('TRACK_TO'); c.target = alvo; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    for loc, en, sz in (((-250, -300, 350), 400000, 300), ((300, -200, 150), 150000, 300), ((0, 300, 300), 120000, 300)):
        l = bpy.data.lights.new('l', 'AREA'); l.energy = en; l.size = sz
        lo = bpy.data.objects.new('l', l); sc.collection.objects.link(lo); lo.location = loc
        c = lo.constraints.new('TRACK_TO'); c.target = alvo; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)
if __name__ == '__main__':
    d = sys.argv[1]
    for i in [int(a) for a in sys.argv[2:]]: render(i, f'r_{i}.png', d)
