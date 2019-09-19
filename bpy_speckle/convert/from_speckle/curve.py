import bpy
from .object import add_custom_properties, add_material
from mathutils import Vector

CONVERT = {}


def import_line(scurve, bcurve, scale):

    if "value" in scurve.keys():
        value = scurve["value"]

        line = bcurve.splines.new('POLY')
        line.points.add(1)

        line.points[0].co = (float(value[0]) * scale, float(value[1]) * scale, float(value[2]) * scale, 1)
        line.points[1].co = (float(value[3]) * scale, float(value[4]) * scale, float(value[5]) * scale, 1)

        return line

CONVERT["Line"] = import_line

def import_polyline(scurve, bcurve, scale):

    if "value" in scurve.keys():
        value = scurve["value"]
        N = int(len(value) / 3)

        polyline = bcurve.splines.new('POLY')

        if "closed" in scurve.keys():
            polyline.use_cyclic_u = scurve["closed"]

        polyline.points.add(N - 1)
        for i in range(0, N):
            polyline.points[i].co = (float(value[i * 3]) * scale, float(value[i * 3+ 1]) * scale, float(value[i * 3+ 2]) * scale, 1)

        return polyline

CONVERT["Polyline"] = import_polyline

def import_nurbs_curve(scurve, bcurve, scale):

    if "points" in scurve.keys():
        points = scurve["points"]
        N = int(len(points) / 3)

        nurbs = bcurve.splines.new('NURBS')


        if "closed" in scurve.keys():
            nurbs.use_cyclic_u = scurve["closed"]

        nurbs.points.add(N - 1)
        for i in range(0, N):
            nurbs.points[i].co = (float(points[i * 3]) * scale, float(points[i * 3+ 1]) * scale, float(points[i * 3+ 2]) * scale, 1)

        nurbs.use_endpoint_u = True
        nurbs.order_u = scurve['degree'] + 1
                
        return nurbs   

CONVERT["Curve"] = import_nurbs_curve

def import_arc(rcurve, bcurve, scale):

    print(rcurve)

    spt = Vector(rcurve['startPoint']['value']) * scale
    ept = Vector(rcurve['endPoint']['value']) * scale
    cpt = Vector(rcurve['plane']['origin']['value']) * scale

    r1 = spt - cpt
    r2 = ept - cpt

    r1.normalize()
    r2.normalize()

    d = rcurve['radius'] * rcurve['angleRadians'] * scale

    normal = r1.cross(r2)

    t1 = normal.cross(r1)
    t2 = normal.cross(r2)

    '''
    Temporary arc
    '''
    arc = bcurve.splines.new('NURBS')

    arc.use_cyclic_u = False

    arc.points.add(3)

    arc.points[0].co = (spt.x, spt.y, spt.z, 1)

    sspt = spt + t1 * d * 0.33
    arc.points[1].co = (sspt.x, sspt.y, sspt.z, 1)

    eept = ept - t2 * d * 0.33
    arc.points[2].co = (eept.x, eept.y, eept.z, 1)

    arc.points[3].co = (ept.x, ept.y, ept.z, 1)

    '''
    print("ARC")
    print("    StartPoint:", rcurve.Arc.StartPoint)
    print("      EndPoint:", rcurve.Arc.EndPoint)
    print("        Center:", rcurve.Arc.Center)
    print("        Radius:", rcurve.Radius)
    '''

    arc.use_endpoint_u = True
    arc.order_u = 3    

    return arc

CONVERT["Arc"] = import_arc

def import_null(speckle_object, bcurve, scale):
    print("Failed to convert type", speckle_object['type'])
    return None

def import_polycurve(scurve, bcurve, scale):

    segments = scurve.get("segments", [])

    for seg in segments:
        speckle_type = seg.get("type", "")

        if speckle_type in CONVERT.keys():
            CONVERT[speckle_type](seg, bcurve, scale)
        else:
            print("Unsupported curve type: {}".format(speckle_type))

CONVERT['Polycurve'] = import_polycurve

def import_curve(speckle_curve, scale):
    name = speckle_curve.get('geometryHash', None)
    if name == None:
        name = speckle_curve.get("_id", None)
        if name == None:
            name = "SpeckleCurve"

    curve_data = bpy.data.curves.new(name, type="CURVE")
    name = speckle_curve['_id']

    curve_data.dimensions = '3D'
    curve_data.resolution_u = 2

    if speckle_curve["type"] not in CONVERT.keys():
        print("Unsupported curve type: {}".format(speckle_curve["type"]))
        return None

    CONVERT[speckle_curve["type"]](speckle_curve, curve_data, scale)

    obj = bpy.data.objects.new(name, curve_data)

    add_material(speckle_curve, obj)
    add_custom_properties(speckle_curve, obj)

    return obj
