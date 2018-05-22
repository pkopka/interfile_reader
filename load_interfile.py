import numpy as np
import pylab
import re
from os import path

def interfile_parser(file_name):
    """
    Parse interfile header to dict
    :param file_name: srt interfile path
    :return:
    """
    f = open(file_name, 'r')
    param={}
    for line in f.readlines():
        matchObj = re.match(r'(.*) := (.*)',line, re.M|re.I)
        if matchObj:
            param[matchObj.group(1)] = matchObj.group(2)
    try:
        param['size']= (int(param['!matrix size [3]']),int(param['!matrix size [2]']),int(param['!matrix size [1]']))
    except KeyError:
        raise  Exception("Bad parsing Matrix size")

    if param['!number format'] == 'float':
        if param['!number of bytes per pixel'] == '4':
            param["type"]=np.float32
        else:
            raise Exception("Bad number format")
    else:
        raise Exception("Bad number format")

    param['path_to_data_file'] = path.join( path.dirname(file_name),param['name of data file'])
    return param

def interfile2array(param):
    """
    conveft interfile to numpy array
    :param param: dict contens interfile poarametrs
    :return:
    """
    # print(param['path_to_data_file'])
    f = open(param['path_to_data_file'], 'r')
    v_list = np.fromfile(f, dtype=param['type'])
    # print('number of voxels', len(v_list))
    f.close()
    resh_arr = np.asarray(v_list).reshape(param['size'])
    return resh_arr


def draw_roi_cm(array,x0,y0,radius,sf,size):
    def cm2pix(dm, dx=sf, size=size):
        return int(size / 2 + (dm * (1/sf))/2.0)

    roi = get_roi(array,cm2pix(x0),cm2pix(-y0),int(radius*(1/sf)))# -y ishow images
    print("Print BV %.2f" % float(np.std(roi)/np.mean(roi)))
    print("Number of pixel ", len(roi))
    draw_roi(array,cm2pix(x0),cm2pix(-y0),int(radius*(1/sf)))# -y ishow images


def draw_roi(array,x0,y0, radius):
    y, x = np.ogrid[-radius: radius, -radius: radius]
    index = (x ** 2 + y ** 2 < radius ** 2) & (x ** 2 + y ** 2 > (radius-1) ** 2)
    value = max(array.flatten())
    array[y0 - radius:y0 + radius, x0 - radius:x0 + radius][index]=value

def get_roi(array,x0,y0, radius):
    y, x = np.ogrid[-radius: radius, -radius: radius]
    index = x ** 2 + y ** 2 <= radius ** 2
    return array[y0 - radius:y0 + radius, x0 - radius:x0 + radius][index]


def show_xy(array,r=437.3):

    pylab.figure()
    mini  =min(array.flatten())
    array=(array-min(array.flatten()))
    array = array/max(array.flatten())*4 #normalize
    pylab.imshow(array, cmap="hot", origin='upper',extent=[-r,r,-r,r])
    pylab.xlabel('X [mm]')
    pylab.ylabel('Y [mm]')
    pylab.xlim([-r,r])
    pylab.colorbar()
    pylab.show()

def show_zx(array,r=437.3,z=250):

    pylab.figure()
    mini  =min(array.flatten())
    array=(array-min(array.flatten()))
    array = array/max(array.flatten())*4 #normalize
    pylab.imshow(array, cmap="hot", origin='upper',extent=[-r,r,-z,z])
    pylab.xlabel('X [mm]')
    pylab.ylabel('Z [mm]')
    pylab.xlim([-r,r])
    pylab.colorbar()
    pylab.show()

if __name__== "__main__":

    # param = interfile_parser('../nema_phatom/my_test_root_image_FBP3DRP.hv')
    param = interfile_parser('../nema_phatom/OSMA/out_file_12.hv')
    # param = interfile_parser('../nema_phatom/OSMA_zero/out_file_12.hv')

    resh_arr = interfile2array(param)

    slice_xy = resh_arr[57,:,:]
    # slice_zx = resh_arr[:,64,:]
    print(float(param['scaling factor (mm/pixel) [1]']),param['size'][1])


    draw_roi_cm(slice_xy,-170,-90,40,float(param['scaling factor (mm/pixel) [1]']),param['size'][1])
    show_xy(slice_xy)

