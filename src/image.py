# Script for performing image processing tasks like downsampling, cropping, and normalization.
from __future__ import division, print_function
import numpy as np

# Downsampling reduces the size of an image by lowering its resolution. So, we want the most important features of image by reducing the dimension
# Process is by using Fourier transform to convert image to frequency domain and removing high frequency components.
def downsample(x, factor=1, shape=None):
    if shape is None:
        m,n = x.shape[-2:] # New dimensions of image
        m = int(m/factor)
        n = int(n/factor)
        shape = (m,n)
    F = np.fft.rfft2(x) # 2D Fourier transform is applied to image 'x'.
    m,n = shape
    A = F[...,0:m//2,0:n//2+1]
    B = F[...,-m//2:,0:n//2+1]
    F = np.concatenate([A,B], axis=-2) # Keep only low frequencies
    ## scale the signal from downsampling to ensure that the energy of the image remains consistent after downsampling.
    a = n*m
    b = x.shape[-2]*x.shape[-1]
    F *= (a/b)
    f = np.fft.irfft2(F, s=shape) # IFT to convert the image back to the spatial domain with reduced resolution.
    return f.astype(x.dtype)

# For cropping the image and extracting a central region from an image or stack.
def crop(stack, size):
    if len(stack.shape) > 2:
        n,m = stack.shape[-2:]
    else:
        n,m = stack.shape
    si = (n-size)//2
    ei = si + size
    sj = (m-size)//2
    ej = sj + size
    stack = stack[...,si:ei,sj:ej]
    return stack

def normalize(stack, radius=None):
    n,m = stack.shape[-2:]
    if radius is None:
        radius = min(n,m)/2
    center = np.array([n/2, m/2])
    y_coord, x_coord = np.ogrid[:n,:m]
    dist = np.sqrt((center[0] - y_coord)**2 + (center[1] - x_coord)**2)
    mask = dist >= radius
    normed = np.zeros_like(stack)
    for i in range(stack.shape[0]):
        mu = stack[i][mask].mean()
        std = stack[i][mask].std()
        normed[i] = (stack[i] - mu)/std
    return normed
