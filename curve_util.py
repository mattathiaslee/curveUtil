import maya.cmds as cmds

#--------------------------------------------------------------------------------
### COMBINE CURVES ###
#--------------------------------------------------------------------------------
def combine_curves(curves, name=None):
    """
    Curves: Takes in a list curve transforms
    Returns: Combined Curve Transform's String Name
    """
    if name == None:
        name = "combined curve"
    grp = cmds.group(em=True, n=name)
    
    for i in curves:
        cmds.makeIdentity(apply=True, t=True, r=True, s=True)
        shapes = cmds.listRelatives(i, shapes=True)[0]
        cmds.parent(shapes, grp, r=True, s=True)
        cmds.delete(i)
        
    grp_shps = cmds.listRelatives(grp)
    for i in grp_shps:
        cmds.rename(i, str(grp) + 'Shape')
        
    return grp



#--------------------------------------------------------------------------------
### GET CURVE DATA ###
"""
Examples:

cube = {'name': 'cube', 
		'shape00': {'degree': 1, 
					'spans': 7, 
					'form': 0, 
					'knots': 8, 
					'cv_list': [(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5)]
					}, 
		'shape01': {'degree': 1, 
					'spans': 7, 
					'form': 0, 
					'knots': 8, 
					'cv_list': [(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5)]
					}
		}
		
triangle = {'name': 'triangle', 
			'shape00': {'degree': 1, 
						'spans': 7, 
						'form': 0, 
						'knots': 8, 
						'cv_list': [(0.0, 0.8164966106414795, 0.0), (-0.28867509961128235, 0.0, -0.5), (-0.2886751592159271, 0.0, 0.5), (0.0, 0.8164966106414795, 0.0), (0.5773502588272095, 0.0, 0.0), (-0.28867509961128235, 0.0, -0.5), (-0.2886751592159271, 0.0, 0.5), (0.5773502588272095, 0.0, 0.0)]
						}
			}
			
pyramid = {'name': 'pyramid', 
			'shape00': {'degree': 1, 
						'spans': 9, 
						'form': 0, 
						'knots': 10, 
						'cv_list': [(-0.7071067690849304, 0.0, 0.0), (0.0, 0.0, 0.7071067690849304), (0.7071067690849304, 0.0, 0.0), (0.0, 0.0, -0.7071067690849304), (-0.7071067690849304, 0.0, 0.0), (0.0, 0.7071067690849304, 0.0), (0.0, 0.0, 0.7071067690849304), (0.7071067690849304, 0.0, 0.0), (0.0, 0.7071067690849304, 0.0), (0.0, 0.0, -0.7071067690849304)]
						}
			}
"""
#--------------------------------------------------------------------------------
def get_shape_data(curve_obj, name):
	"""
	Format: {'name:', 
			'shape00': {degree: int,
						spans: int,
						form: int,
						knots: int,
						cv_list: []
						},
			'shape01': {degree: int,
						spans: int,
						form: int,
						knots: int,
						cv_list: []
						},
			}

	"""

    data = {}
    data["name"] = name
    cmds.delete(selection, ch=True)  # Enable Cvs to "bake" 
    curveShapes = cmds.listRelatives(selection, shapes=True, type="nurbsCurve", f=True)
    
    count = 0
    for shape in curveShapes:
        shapeData = {}
        
        degree = cmds.getAttr(shape + ".degree")
        spans = cmds.getAttr(shape + ".spans")
        form = cmds.getAttr(shape + ".form")
        cv_count = degree + spans
        knots = cv_count + degree - 1
        
        cv_list = []
        cvs = cmds.ls("{}.cv[*]".format(shape), l=True)[0]
        cv_list = cmds.getAttr(cvs)
        
        shapeData["degree"] = degree
        shapeData["spans"] = spans
        shapeData["form"] = form
        shapeData["knots"] = knots
        shapeData["cv_list"] = cv_list
        
        shapeIdx = "shape0" + str(num)
        data[shapeIdx] = shapeData
        count+=1
     
    return data


#--------------------------------------------------------------------------------
### CREATE SINGLE CURVE ###
#--------------------------------------------------------------------------------
def create_single_curve(data, name):
    """
    Returns Created Curve Transform's String Name
    """
    name = name
    degree = data["degree"]
    spans = data["spans"]
    form = data["form"]
    knots = data["knots"]
    cv_list = data["cv_list"]
    cv_knots = []
    
    if form == 0:  # curve is open
        if degree == 1: #  curve is linear
            for i in range (0, knots):
                cv_knots.append(i)
        else:  # curve is cubic
            knot_iter = 0
            for i in range(0, knots):
                if i >= 3 and i <= knots-3:
                    knot_iter += 1
                cv_knots.append(knot_iter)

    elif form == 2:  # Periodic Curve
        for i in range(3):
            cv_list.append(cv_list[i])  # appends the first 3 CV coordinates to the end of cv_list

        for i in range(knots):
            cv_knots.append(i-2)  # Shifts down the list down by 2
    
    created_curve = cmds.curve(per=form, d=degree, p=cv_list, k=cv_knots, n=name)
    created_curve_shapes = cmds.listRelatives(created_curve)[0]
    cmds.rename(created_curve_shapes, str(created_curve) + 'Shape')
    return created_curve



#--------------------------------------------------------------------------------
### CREATE CURVE FROM DATA ###
#--------------------------------------------------------------------------------
def create_curve(data):
    if not isinstance(data, dict):
        pass
    else:
        created_shapes = []
        for key in data:
            if 'name' in key:
                name=data[key]
            else:
                shape = data[key]
                created_shp = (create_single_curve(shape, name='tempt'))
                created_shapes.append(created_shp)
        final_curve = combine_curves(created_shapes, name=name)
        cmds.select(final_curve)  
        return final_curve
