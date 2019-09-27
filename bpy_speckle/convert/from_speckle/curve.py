import bpy, math
from bpy_speckle.util import find_key_case_insensitive
from mathutils import Vector, Quaternion

CONVERT = {}


def import_line(scurve, bcurve, scale):

    value = find_key_case_insensitive(scurve, "value")

    if value:

        line = bcurve.splines.new('POLY')
        line.points.add(1)

        line.points[0].co = (float(value[0]) * scale, float(value[1]) * scale, float(value[2]) * scale, 1)
        line.points[1].co = (float(value[3]) * scale, float(value[4]) * scale, float(value[5]) * scale, 1)

        return line

CONVERT["Line"] = import_line

def import_polyline(scurve, bcurve, scale):

    value = find_key_case_insensitive(scurve, "value")

    if value:
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

    points = find_key_case_insensitive(scurve, "points")

    if points:
        N = int(len(points) / 3)

        nurbs = bcurve.splines.new('NURBS')

        nurbs.use_cyclic_u = find_key_case_insensitive(scurve, "closed", False)

        nurbs.points.add(N - 1)
        for i in range(0, N):
            nurbs.points[i].co = (float(points[i * 3]) * scale, float(points[i * 3+ 1]) * scale, float(points[i * 3+ 2]) * scale, 1)

        nurbs.use_endpoint_u = True
        nurbs.order_u = scurve['degree'] + 1
                
        return nurbs   

CONVERT["Curve"] = import_nurbs_curve

def import_arc(rcurve, bcurve, scale):

    '''
    Parse arc data from Speckle object dictionary
    '''
    plane = find_key_case_insensitive(rcurve, "plane")
    if not plane:
        return

    origin = find_key_case_insensitive(plane, "origin")
    normal = find_key_case_insensitive(plane, "normal")
    normal = Vector(find_key_case_insensitive(normal, "value"))

    xaxis = find_key_case_insensitive(plane, "xdir")
    yaxis = find_key_case_insensitive(plane, "ydir")

    radius = find_key_case_insensitive(rcurve, "radius", 0) * scale
    startAngle = find_key_case_insensitive(rcurve, "startAngle", 0)
    endAngle = find_key_case_insensitive(rcurve, "endAngle", 0)

    startQuat = Quaternion(normal, startAngle)
    endQuat = Quaternion(normal, endAngle)

    '''
    Get start and end vectors, centre point, angles, etc.
    '''

    r1 = Vector(find_key_case_insensitive(xaxis, "value"))
    r1.rotate(startQuat)

    r2 = Vector(find_key_case_insensitive(xaxis, "value"))
    r2.rotate(endQuat)

    c = Vector(find_key_case_insensitive(origin, "value")) * scale

    spt = c + r1 * radius
    ept = c + r2 * radius

    #d = radius * (endAngle - startAngle)
    angle = endAngle - startAngle

    t1 = normal.cross(r1)
    #t2 = normal.cross(r2)

    '''
    Initialize arc data and calculate subdivisions
    '''
    arc = bcurve.splines.new('NURBS')

    arc.use_cyclic_u = False

    Ndiv = max(int(math.floor(angle / 0.3)), 2)
    step = angle / float(Ndiv)
    stepQuat = Quaternion(normal, step)
    tan = math.tan(step / 2) * radius

    arc.points.add(Ndiv + 1)

    '''
    Set start and end points
    '''
    arc.points[0].co = (spt.x, spt.y, spt.z, 1)
    arc.points[Ndiv + 1].co = (ept.x, ept.y, ept.z, 1)

    '''
    Set intermediate points
    '''
    for i in range(Ndiv):
        t1 = normal.cross(r1)
        pt = c + r1 * radius + t1 * tan
        arc.points[i + 1].co = (pt.x, pt.y, pt.z, 1)
        r1.rotate(stepQuat)

    '''
    Set curve settings
    '''

    arc.use_endpoint_u = True
    arc.order_u = 3    

    return arc

CONVERT["Arc"] = import_arc

def import_null(speckle_object, bcurve, scale):
    print("Failed to convert type", speckle_object['type'])
    return None

def import_polycurve(scurve, bcurve, scale):

    segments = find_key_case_insensitive(scurve, "segments")

    for seg in segments:
        speckle_type = seg.get("type", "")

        if speckle_type in CONVERT.keys():
            CONVERT[speckle_type](seg, bcurve, scale)
        else:
            print("Unsupported curve type: {}".format(speckle_type))

CONVERT['Polycurve'] = import_polycurve

def import_curve(speckle_curve, scale, name=None):
    if not name:
        name = speckle_curve.get('geometryHash', None)
        if name == None:
            name = speckle_curve.get("_id", None)
            if name == None:
                name = "SpeckleCurve"

    if name in bpy.data.curves.keys():
        curve_data = bpy.data.curves[name]
    else:
        curve_data = bpy.data.curves.new(name, type="CURVE")

    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12

    if speckle_curve["type"] not in CONVERT.keys():
        print("Unsupported curve type: {}".format(speckle_curve["type"]))
        return None

    CONVERT[speckle_curve["type"]](speckle_curve, curve_data, scale)

    return curve_data
