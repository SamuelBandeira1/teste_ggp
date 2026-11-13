import sys, os, pickle, numpy as np, trimesh, bpy, bmesh
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union
sys.path.insert(0, '.')
import vetor
NOME = {1:'engrenagem-codigo',2:'escudo-aperto-de-mao',3:'formatura-anime',4:'sol-calculadora-grafico',
        5:'cafe-oculos',6:'capacete-bandeira',7:'camaleao',8:'haltere-folha-oculos',9:'leitura-relogio'}
ESP, CHANF, ESP_IN, ESP_F = 14.0, 1.8, 13.0, 6.0
PINO = (15.0, 8.0, 8.0)
CORTE = 0.6

def polys(g):
    if g.is_empty: return []
    return [p for p in (g.geoms if hasattr(g, 'geoms') else [g]) if p.geom_type == 'Polygon' and p.area > 0.3]

def geometria(i):
    if i == 9:
        d = pickle.load(open('i9_vetor.pkl', 'rb')); p, b, f = d['preto'], d['branco'], Polygon()
    else:
        H = int(open(f'i{i}_altura.txt').read())
        ler = lambda n: vetor.ler(f'i{i}_{n}.svg', H) if os.path.exists(f'i{i}_{n}.svg') else Polygon()
        p, b, f = ler('preto'), ler('branco'), ler('fundo')
    clip = box(-46 if i == 1 else -200, CORTE, 200, 300)      # no 1, corta o texto '10 cm' da imagem de referência
    sh = lambda g: __import__('shapely').affinity.translate(g.intersection(clip), 0, -CORTE)
    p, b, f = sh(p.buffer(0)), sh(b.buffer(0)), sh(f.buffer(0))
    b = b.difference(p); f = f.difference(p).difference(b)
    # tira fragmentos soltos longe da peça (textos e pedaços da imagem de referência)
    tudo = unary_union([p, b, f]); comps = polys(tudo)
    if comps:
        maior = max(comps, key=lambda c: c.area)
        lixo = unary_union([c for c in comps if c is not maior and c.area < 40 and c.distance(maior) > 2.0])
        if not lixo.is_empty: p, b, f = p.difference(lixo), b.difference(lixo), f.difference(lixo)
    return p, b, f

def extrudar(g, h):
    ms = [trimesh.creation.extrude_polygon(pg, h) for pg in polys(g)]
    return trimesh.util.concatenate(ms) if ms else None

def para_blender(m, nome):
    me = bpy.data.meshes.new(nome); me.from_pydata(m.vertices.tolist(), [], m.faces.tolist()); me.update()
    ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob); return ob

def chanfrar(ob, z, off):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.normal_update()
    ar = [e for e in bm.edges if all(abs(v.co.z - z) < 1e-4 for v in e.verts) and len(e.link_faces) == 2
          and abs(e.link_faces[0].normal.z) + abs(e.link_faces[1].normal.z) < 1.5]
    bmesh.ops.bevel(bm, geom=ar, offset=off, offset_type='OFFSET', segments=5, profile=0.5, affect='EDGES', clamp_overlap=True)
    bm.to_mesh(ob.data); bm.free()

def bool_(a, b, op):
    m = a.modifiers.new('b', 'BOOLEAN'); m.object = b; m.operation = op; m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = a
    for o in bpy.data.objects: o.select_set(o == a)
    bpy.ops.object.modifier_apply(modifier='b')

def malha(ob):
    me = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    v = np.array([x.co[:] for x in me.vertices]); f = []
    for poly in me.polygons:
        vs = list(poly.vertices)
        for k in range(1, len(vs)-1): f.append([vs[0], vs[k], vs[k+1]])
    return trimesh.Trimesh(v, np.array(f), process=True)

def icone(i, out, mont):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    p, b, f = geometria(i)
    # checa se tudo está ligado ao pino
    tudo = unary_union([p, b, f]); comp = polys(tudo)
    pino2d = box(-PINO[0], -0.1, PINO[0], 0.5)
    soltos = [c for c in comp if not c.intersects(pino2d) and c.area > 2]
    preto = para_blender(extrudar(p, ESP), 'preto')
    chanfrar(preto, ESP, CHANF)
    pino = para_blender(trimesh.creation.box(extents=(2*PINO[0], PINO[1]+0.6, PINO[2]),
                         transform=trimesh.transformations.translation_matrix((0, -(PINO[1]-0.6)/2, PINO[2]/2))), 'pino')
    mp = trimesh.util.concatenate([malha(preto), malha(pino)])     # o fatiador une as duas cascas (mesmo objeto)
    partes = {'preto': mp}
    brancos = [m for m in (extrudar(b, ESP_IN), extrudar(f, ESP_F)) if m is not None]
    if brancos: partes['branco'] = trimesh.util.concatenate(brancos)
    nome = f'trofeu-{i}-{NOME[i]}'
    sc = trimesh.Scene()
    for k, m in partes.items():
        m.visual.face_colors = [20,20,20,255] if k == 'preto' else [245,245,245,255]
        sc.add_geometry(m, node_name=k, geom_name=k); m.export(os.path.join(mont, f'{nome}-{k}.stl'))
    sc.export(os.path.join(out, nome + '.3mf'))
    print(f"{i} {NOME[i]:<24} {mp.extents.round(0)} preto_ok={mp.is_watertight} soltos={len(soltos)} faces={len(mp.faces)}", flush=True)

if __name__ == '__main__':
    out, mont = sys.argv[1], sys.argv[1] + '_deitado'
    os.makedirs(out, exist_ok=True); os.makedirs(mont, exist_ok=True)
    for i in [int(a) for a in sys.argv[2:]] or range(1, 10): icone(i, out, mont)
