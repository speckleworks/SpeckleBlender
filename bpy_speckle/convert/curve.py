import bpy
from .object import add_custom_properties, add_material

def import_line(scurve, bcurve, scale):

    if "value" in scurve.keys():
        value = scurve["value"]

        line = bcurve.splines.new('POLY')
        line.points.add(1)

        line.points[0].co = (float(value[0]) * scale, float(value[1]) * scale, float(value[2]) * scale, 1)
        line.points[1].co = (float(value[3]) * scale, float(value[4]) * scale, float(value[5]) * scale, 1)

        return line

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

def import_nurbs_curve(scurve, bcurve, scale):

    if "points" in scurve.keys():
        points = scurve["points"]
        N = int(len(points) / 3)

        print(scurve)

        nurbs = bcurve.splines.new('NURBS')
        #nurbs.use_bezier_u = True
        nurbs.use_endpoint_u = True
        nurbs.order_u = scurve['degree'] + 1

        if "closed" in scurve.keys():
            nurbs.use_cyclic_u = scurve["closed"]

        nurbs.points.add(N - 1)
        for i in range(0, N):
            nurbs.points[i].co = (float(points[i * 3]) * scale, float(points[i * 3+ 1]) * scale, float(points[i * 3+ 2]) * scale, 1)

        return nurbs        

def import_null(speckle_object, bcurve, scale):
    print(speckle_object['type'])
    print(speckle_object)
    print()

CONVERT = {
    "Curve": import_nurbs_curve,
    "Line": import_line,
    "Polyline": import_polyline,
    "Arc":import_null
}

def import_polycurve(scurve, bcurve, scale):

    if "segments" in scurve.keys():

        segments = scurve["segments"]
        for seg in segments:

            if "type" in seg.keys():
                speckle_type = seg["type"]

                if speckle_type in CONVERT.keys():
                    CONVERT[speckle_type](seg, bcurve, scale)

CONVERT['Polycurve'] = import_polycurve

def import_curve(speckle_curve, scale):
    name = speckle_curve['_id']

    curve_data = bpy.data.curves.new(name, type="CURVE")
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 2

    CONVERT[speckle_curve["type"]](speckle_curve, curve_data, scale)

    #print("Curve type: {}".format(speckle_curve["type"]))

    obj = bpy.data.objects.new(name, curve_data)

    add_material(speckle_curve, obj)
    add_custom_properties(speckle_curve, obj)

    return obj             